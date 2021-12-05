"""公共解析函数"""
import inspect
from typing import Dict, Type, Callable, List, Tuple, Any
from pydantic import BaseModel
from .models.apispec import OPENAPI3_REF_TEMPLATE, OPENAPI3_REF_PREFIX
from .models.paths import Operation, Parameter, ParameterInType, Schema, Response, PathItem, MediaType, UnprocessableEntity
from .status import HTTP_STATUS


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


def get_func_parameter(func: Callable, arg_name='path') -> Type[BaseModel]:
    """Get view-func parameters.
    arg_name has six parameters to choose from: path, query, form, body, header, cookie.
    """
    signature = inspect.signature(func)
    p = signature.parameters.get(arg_name)
    return p.annotation if p else None


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


def parse_func_info(func, components_schemas):
    """函数信息解析 参数 文档..."""
    parameters = []
    operation = get_operation(func)
    query = get_func_parameter(func, 'query')
    if query:
        _parameters, _components_schemas = parse_query(query)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)

    operation.parameters = parameters if parameters else None
    func.operation = operation
    return query


def bind_rule_swagger(url_map, view_funcs, components_schemas, paths):
    register_methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')  # 只需要记录这五种请求方式

    for url_rule in url_map.iter_rules():
        path = url_rule.rule
        func = view_funcs[url_rule.endpoint]
        methods = url_rule.methods

        if not getattr(func, '_swagger', False):  # 不需要swagger处理的接口
            continue

        for method in register_methods:
            if method in methods:
                get_responses({}, components_schemas, func.operation)
                bind_path_method_info(path, method, paths, func.operation)
