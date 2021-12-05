from enum import Enum
from typing import Union, Dict
from pydantic import BaseModel, Field


class SecuritySchemeType(str, Enum):
    apiKey = 'apiKey'
    http = 'http'
    oauth2 = 'oauth2'
    openIdConnect = 'openIdConnect'


class SecurityBase(BaseModel):
    type_: SecuritySchemeType = Field(..., alias='type')
    description: str = None


class APIKeyIn(str, Enum):
    query = 'query'
    header = 'header'
    cookie = 'cookie'


class APIKey(SecurityBase):
    type_ = Field(default=SecuritySchemeType.apiKey, alias='type')
    in_: APIKeyIn = Field(..., alias='in')
    name: str


class HTTPBase(SecurityBase):
    type_ = Field(default=SecuritySchemeType.http, alias='type')
    scheme: str


class HTTPBearer(HTTPBase):
    scheme = 'bearer'
    bearerFormat: str = None


class OAuthFlow(BaseModel):
    refreshUrl: str = None
    scopes: Dict[str, str] = {}


class OAuthFlowImplicit(OAuthFlow):
    authorizationUrl: str


class OAuthFlowPassword(OAuthFlow):
    tokenUrl: str


class OAuthFlowClientCredentials(OAuthFlow):
    tokenUrl: str


class OAuthFlowAuthorizationCode(OAuthFlow):
    authorizationUrl: str
    tokenUrl: str


class OAuthFlows(BaseModel):
    implicit: OAuthFlowImplicit = None
    password: OAuthFlowPassword = None
    clientCredentials: OAuthFlowClientCredentials = None
    authorizationCode: OAuthFlowAuthorizationCode = None


class OAuth2(SecurityBase):
    type_ = Field(default=SecuritySchemeType.oauth2, alias='type')
    flows: OAuthFlows


class OpenIdConnect(SecurityBase):
    type_ = Field(default=SecuritySchemeType.openIdConnect, alias='type')
    openIdConnectUrl: str


SecurityScheme = Union[APIKey, HTTPBase, OAuth2, OpenIdConnect, HTTPBearer]
