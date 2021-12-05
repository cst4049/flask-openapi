from pydantic import BaseModel, AnyUrl, Field


class ExternalDocumentation(BaseModel):
    url: AnyUrl = Field(None, title='外部链接url')
    description: str = Field(None, title='链接描述信息')
