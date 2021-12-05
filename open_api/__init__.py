import json
from pydantic import AnyUrl
from .models import APISpec, Components, ExternalDocumentation, Info, SecurityScheme


class OpenApi:
    def __init__(self, app):
        self.app = app
        self.tags = []
        self.api_name = 'openapi'
        self.openapi_version = '3.0.3'
        self.info = Info(title='OpenAPI', version='1.0.0')
        self.api_json_url = f'/{self.api_name}/{self.api_name}.json'
        self.markdown_url = f'/{self.api_name}/markdown'
        self.components = Components()
        self.components_schemas = {}
        self.externalDocs = ExternalDocumentation(
            url=AnyUrl(
                url=f'/{self.api_name}/markdown',
                scheme='',
                host=''
                ),
            description='Export to markdown')
        self.openapi = '3.0.3'
        self.paths = dict()

        self.securitySchemes = SecurityScheme

    def api_doc(self):
        spec = APISpec(
            openapi=self.openapi_version,
            info=self.info,
            externalDocs=self.externalDocs
        )
        # spec.tags = self.tags or None
        spec.paths = self.paths
        self.components.schemas = self.components_schemas
        spec.components = self.components
        return json.loads(spec.json(by_alias=True, exclude_none=True))
