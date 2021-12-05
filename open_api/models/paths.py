from enum import Enum
from typing import List, Dict, Union
from pydantic import BaseModel, Field
from .swagger import Reference, MediaType, Response, Schema


class ParameterInType(str, Enum):
    query = 'query'
    header = 'header'
    path = 'path'
    cookie = 'cookie'


class Parameter(BaseModel):
    name: str
    in_: ParameterInType = Field(..., alias="in")  # ... is REQUIRED
    description: str = None
    required: bool = None
    schema_: Union[Schema, Reference] = Field(None, alias="schema")


class RequestBody(BaseModel):
    description: str = None
    content: Dict[str, MediaType]
    required: bool = Field(default=True)


class Operation(BaseModel):
    tags: List[str] = None
    summary: str = None
    description: str = None
    parameters: List[Union[Parameter, Reference]] = None
    requestBody: Union[RequestBody, Reference] = None
    responses: Dict[str, Response] = None
    security: List[Dict[str, List[str]]] = None


class PathItem(BaseModel):
    ref: str = Field(None, alias="$ref")
    summary: str = None
    description: str = None
    get: Operation = None
    put: Operation = None
    post: Operation = None
    delete: Operation = None
    options: Operation = None
    head: Operation = None
    patch: Operation = None
    trace: Operation = None
