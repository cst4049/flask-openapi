from pydantic import BaseModel, AnyUrl, Field


class Contact(BaseModel):
    name: str = Field(None, title='联系人')
    url: AnyUrl = Field(None, title='联系url')


class License(BaseModel):
    name: str = Field(None, title='版权')
    identifier: str = Field(None, title='版权者')
    url: AnyUrl = Field(None, title='版权地址')


class Info(BaseModel):
    title: str = Field(None, title='信息标题')
    version: str = Field(None, title='信息版本')
    summary: str = Field(None, title='总结')
    description: str = Field(None, title='描述')
    termsOfService: AnyUrl = Field(None, title='')
    contact: Contact = Field(None, title='联系方式')
    license: License = Field(None, title='版权')
