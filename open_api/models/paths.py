from pydantic import BaseModel, Field


class PathItem(BaseModel):
    pass


class Path(BaseModel):
    path: str = Field(None, title='路经')
