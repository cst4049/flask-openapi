from typing import List, Dict
from pydantic import BaseModel, Field
from .externalDocs import ExternalDocumentation
from .components import Components
from .info import Info
from .paths import PathItem

OPENAPI3_REF_PREFIX = '#/components/schemas'
OPENAPI3_REF_TEMPLATE = OPENAPI3_REF_PREFIX + '/{model}'


class APISpec(BaseModel):
    """swagger openapi.json 格式"""
    openapi: str = Field(..., title='版本')
    info: Info = Field(..., title='详细信息')
    paths: Dict[str, PathItem] = Field(None, title='路经')
    components: Components = Field(None, title='组件schema信息')
    security: List[Dict[str, List[str]]] = Field(None, title='安全信息')
    externalDocs: ExternalDocumentation = Field(None, title='外部链接')
