"""公共解析函数"""
import inspect
from typing import Type, Dict, Callable, List, Tuple, Any
from pydantic import BaseModel
from .models.apispec import OPENAPI3_REF_TEMPLATE, OPENAPI3_REF_PREFIX
from .models.paths import Operation, Parameter, ParameterInType, Schema, Response, PathItem, MediaType, \
    UnprocessableEntity, RequestBody
from .status import HTTP_STATUS
from werkzeug.routing import parse_rule

from http import HTTPStatus
from flask import Response as _Response


Response_422 = Response(
    description=HTTP_STATUS["422"],
    content={
        "application/json": MediaType(
            **{"schema": Schema(
                **{"type": "array",
                   "items": {"$ref": f"{OPENAPI3_REF_PREFIX}/{UnprocessableEntity.__name__}"}
                   }
            )
            }
        )
    }
)
Response_500 = Response(description=HTTP_STATUS["500"])


def _parse_rule(rule: str) -> str:
    """Flask route conversion to openapi:
    /pet/<petId> --> /pet/{petId}
    """
    uri = ''
    for converter, args, variable in parse_rule(str(rule)):
        if converter is None:
            uri += variable
            continue
        uri += "{%s}" % variable
    return uri


def get_operation(func: Callable) -> Operation:
    """Return a Operation object with summary and description."""
    doc = inspect.getdoc(func) or ''
    doc = doc.strip()
    lines = doc.split('\n')
    operation = Operation(
        summary=lines[0] or None,
        description=lines[0] if len(lines) == 0 else '</br>'.join(lines[1:]) or None
    )
    return operation


def get_func_parameter(func: Callable, arg_name='path', type='annotation') -> Type[BaseModel]:
    """Get view-func parameters.
    arg_name has six parameters to choose from: path, query, form, body, header, cookie.
    """
    signature = inspect.signature(func)
    p = signature.parameters.get(arg_name)
    if type == 'annotation':
        return p.annotation if p else None
    return p.default if p else None


def get_schema(obj: Type[BaseModel]) -> dict:
    """Pydantic model conversion to openapi schema"""
    assert inspect.isclass(obj) and \
           issubclass(obj, BaseModel), f"{obj} is invalid `pydantic.BaseModel`"
    return obj.schema(ref_template=OPENAPI3_REF_TEMPLATE)


def parse_query(query: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
    """Parse query model"""
    schema = get_schema(query)
    parameters = []
    components_schemas = dict()
    properties = schema.get('properties')
    definitions = schema.get('definitions')

    if properties:
        for name, value in properties.items():
            data = {
                "name": name,
                "in": ParameterInType.query,
                "description": value.get("description"),
                "required": name in schema.get("required", []),
                "schema": Schema(**value)
            }
            parameters.append(Parameter(**data))
    if definitions:
        for name, value in definitions.items():
            components_schemas[name] = Schema(**value)
    return parameters, components_schemas


def parse_body(body: Type[BaseModel]) -> Tuple[Dict[str, MediaType], dict]:
    """Parse body model"""
    schema = get_schema(body)
    content = None
    components_schemas = dict()
    properties = schema.get('properties')
    definitions = schema.get('definitions')

    if properties:
        title = schema.get('title')
        components_schemas[title] = Schema(**schema)
        content = {
            "application/json": MediaType(
                **{
                    "schema": Schema(
                        **{
                            "$ref": f"{OPENAPI3_REF_PREFIX}/{title}"
                        }
                    )
                }
            )
        }
    if definitions:
        for name, value in definitions.items():
            components_schemas[name] = Schema(**value)
    return content, components_schemas


def parse_path(path: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
    """Parse path model"""
    schema = get_schema(path)
    parameters = []
    components_schemas = dict()
    properties = schema.get('properties')
    definitions = schema.get('definitions')

    if properties:
        for name, value in properties.items():
            data = {
                "name": name,
                "in": ParameterInType.path,
                "description": value.get("description"),
                "required": True,
                "schema": Schema(**value)
            }
            parameters.append(Parameter(**data))
    if definitions:
        for name, value in definitions.items():
            components_schemas[name] = Schema(**value)
    return parameters, components_schemas


def get_responses(responses: dict, components_schemas: dict, operation: Operation) -> None:
    """
    :param responses: Dict[str, BaseModel]
    :param components_schemas: `models.component.py` Components.schemas
    :param operation: `models.path.py` Operation
    """
    if responses is None:
        responses = {}
    _responses = {}
    _schemas = {}
    if not responses.get("422"):
        _responses["422"] = Response_422
        _schemas[UnprocessableEntity.__name__] = Schema(**UnprocessableEntity.schema())
    if not responses.get("500"):
        _responses["500"] = Response_500
    for key, response in responses.items():
        assert inspect.isclass(response) and \
               issubclass(response, BaseModel), f" {response} is invalid `pydantic.BaseModel`"
        schema = response.schema(ref_template=OPENAPI3_REF_TEMPLATE)
        _responses[key] = Response(
            description=HTTP_STATUS.get(key, ""),
            content={
                "application/json": MediaType(
                    **{
                        "schema": Schema(
                            **{
                                "$ref": f"{OPENAPI3_REF_PREFIX}/{response.__name__}"
                            }
                        )
                    }
                )
            }
        )
        _schemas[response.__name__] = Schema(**schema)
        definitions = schema.get('definitions')
        if definitions:
            for name, value in definitions.items():
                _schemas[name] = Schema(**value)

    components_schemas.update(**_schemas)
    operation.responses = _responses


def bind_path_method_info(uri: str, method: str, paths: dict, operation: Operation) -> None:
    """
    :param uri: api route path
    :param method: get post put delete patch
    :param paths: openapi doc paths
    :param operation: `models.path.py` Operation
    """
    if method == 'GET':
        if not paths.get(uri):
            paths[uri] = PathItem(get=operation)
        else:
            paths[uri].get = operation
    elif method == 'POST':
        if not paths.get(uri):
            paths[uri] = PathItem(post=operation)
        else:
            paths[uri].post = operation
    elif method == 'PUT':
        if not paths.get(uri):
            paths[uri] = PathItem(put=operation)
        else:
            paths[uri].put = operation
    elif method == 'PATCH':
        if not paths.get(uri):
            paths[uri] = PathItem(patch=operation)
        else:
            paths[uri].patch = operation
    elif method == 'DELETE':
        if not paths.get(uri):
            paths[uri] = PathItem(delete=operation)
        else:
            paths[uri].delete = operation


def validate_response(resp: Any, responses: Dict[str, Type[BaseModel]]) -> None:
    """Validate response"""
    print("Warning: "
          "You are using `VALIDATE_RESPONSE=True`, "
          "please do not use it in the production environment, "
          "because it will reduce the performance.")
    if isinstance(resp, tuple):  # noqa
        _resp, status_code = resp[:2]
    elif isinstance(resp, _Response):
        if resp.mimetype != "application/json":
            # only application/json
            return
            # raise TypeError("`Response` mimetype must be application/json.")
        _resp, status_code = resp.json, resp.status_code  # noqa
    else:
        _resp, status_code = resp, 200
    if isinstance(status_code, HTTPStatus):
        status_code = status_code.value

    resp_model = responses.get(str(status_code))
    if resp_model is None:
        return
    assert inspect.isclass(resp_model) and \
           issubclass(resp_model, BaseModel), f"{resp_model} is invalid `pydantic.BaseModel`"
    try:
        resp_model(**_resp)
    except TypeError:
        raise TypeError(f"`{resp_model.__name__}` validation failed, must be a mapping.")


def parse_func_info(func, components_schemas, operation):
    """函数信息解析 参数 文档..."""
    parameters = []
    query = get_func_parameter(func, 'query')
    body = get_func_parameter(func, 'body')
    path = get_func_parameter(func, 'path')
    if query:
        _parameters, _components_schemas = parse_query(query)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)
    if body:
        _content, _components_schemas = parse_body(body)
        components_schemas.update(**_components_schemas)
        requestBody = RequestBody(**{
            "content": _content,
        })
        operation.requestBody = requestBody
    if path:
        _parameters, _components_schemas = parse_path(path)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)

    operation.parameters = parameters if parameters else None
    func.operation = operation
    return query, body, path


def add_swagger_info(components_schemas, responses, tags, operation):
    get_responses(responses, components_schemas, operation)
    operation.tags = tags


def bind_rule_swagger(url_map, view_funcs, paths):
    register_methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')  # 只需要记录这五种请求方式

    for url_rule in url_map.iter_rules():
        path = url_rule.rule
        func = view_funcs[url_rule.endpoint]
        methods = url_rule.methods

        if not getattr(func, '_swagger', False):  # 不需要swagger处理的接口
            continue

        path = _parse_rule(path)
        for method in register_methods:
            if method in methods:
                bind_path_method_info(path, method, paths, func.operation)
