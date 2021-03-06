from pydantic import BaseModel
from typing import Dict, Union
from .swagger import Schema, Reference
from .security import SecurityScheme


class Components(BaseModel):
    schemas: Dict[str, Union[Schema, Reference]] = None
    securitySchemes: Dict[str, Union[SecurityScheme, Reference]] = None
