"""公共解析函数"""
import inspect
from http import HTTPStatus
from typing import Dict, Type, Callable, List, Tuple, Any
from pydantic import BaseModel
from .models.apispec import OPENAPI3_REF_TEMPLATE, OPENAPI3_REF_PREFIX
from .models.paths import Operation, Parameter, ParameterInType, Schema, Response, PathItem, MediaType, UnprocessableEntity
from .status import HTTP_STATUS


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
        _responses["422"] = Response(
            description=HTTP_STATUS["422"],
            content={
                "application/json": MediaType(
                    **{
                        "schema": Schema(
                            **{
                                "type": "array",
                                "items": {"$ref": f"{OPENAPI3_REF_PREFIX}/{UnprocessableEntity.__name__}"}
                            }
                        )
                    }
                )
            }
        )
        _schemas[UnprocessableEntity.__name__] = Schema(**UnprocessableEntity.schema())
    if not responses.get("500"):
        _responses["500"] = Response(description=HTTP_STATUS["500"])
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


def parse_method(uri: str, method: str, paths: dict, operation: Operation) -> None:
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
