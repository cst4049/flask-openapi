from pydantic import BaseModel, Field


class ExternalDocumentation(BaseModel):
    url: str = Field(None, title='外部链接url')
    description: str = Field(None, title='链接描述信息')
