from typing import List, Any, Union, Dict
from pydantic import BaseModel, Field


class Reference(BaseModel):
    """引用"""
    ref: str = Field(..., alias="$ref")


class Schema(BaseModel):
    """参数定义"""
    ref: str = Field(None, alias="$ref")
    title: str = None
    multipleOf: float = None
    maximum: float = None
    exclusiveMaximum: float = None
    minimum: float = None
    exclusiveMinimum: float = None
    maxLength: int = Field(None, gte=0)
    minLength: int = Field(None, gte=0)
    pattern: str = None
    maxItems: int = Field(None, gte=0)
    minItems: int = Field(None, gte=0)
    uniqueItems: bool = None
    maxProperties: int = Field(None, gte=0)
    minProperties: int = Field(None, gte=0)
    required: List[str] = None
    enum: List[Any] = None
    type: str = None
    allOf: List[Any] = None
    oneOf: List[Any] = None
    anyOf: List[Any] = None
    not_: Any = Field(None, alias="not")
    items: Any = None
    properties: Dict[str, Any] = None
    additionalProperties: Union[Dict[str, Any], bool] = None
    description: str = None
    format: str = None
    default: Any = None
    nullable: bool = None
    readOnly: bool = None
    writeOnly: bool = None
    # externalDocs: ExternalDocumentation = None
    example: Any = None
    deprecated: bool = None


class Encoding(BaseModel):
    contentType: str = None
    style: str = None
    explode: bool = True
    allowReserved: bool = None


class MediaType(BaseModel):
    schema_: Union[Schema, Reference] = Field(None, alias='schema')
    encoding: Dict[str, Encoding] = None


class Response(BaseModel):
    description: str = None
    content: Dict[str, MediaType] = None
