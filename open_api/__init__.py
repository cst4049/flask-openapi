import os
import json
from pydantic import AnyUrl
from .models import APISpec, Components, ExternalDocumentation, Info, SecurityScheme
from flask import Blueprint, render_template


class OpenApi:
    def __init__(self, app):
        self.app = app
        self.tags = []
        self.api_name = 'openapi'
        self.openapi_version = '3.0.3'
        self.info = Info(title='OpenAPI', version='1.0.0')
        self.api_doc_url = f'//{self.api_name}.json'
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
        self.docExpansion = 'list'
        self.oauth_config = dict()
        self.register_template()

    def register_template(self):
        _here = os.path.dirname(__file__)
        template_folder = os.path.join(_here, 'templates')
        static_folder = os.path.join(template_folder, 'static')

        blueprint = Blueprint(
            self.api_name,
            __name__,
            url_prefix=f'/{self.api_name}',
            template_folder=template_folder,
            static_folder=static_folder
        )
        blueprint.add_url_rule(
            rule=self.api_doc_url,
            endpoint=self.api_name,
            view_func=lambda: self.api_doc
        )
        blueprint.add_url_rule(
            rule='/redoc',
            endpoint='redoc',
            view_func=lambda: render_template("redoc.html", api_doc_url=f'{self.api_name}.json')
        )
        blueprint.add_url_rule(
            rule='/swagger',
            endpoint='swagger',
            view_func=lambda: render_template(
                "swagger.html",
                api_doc_url=f'{self.api_name}.json',
                docExpansion=self.docExpansion,
                oauth_config=self.oauth_config.dict() if self.oauth_config else None
            )
        )
        blueprint.add_url_rule(
            rule='/markdown',
            endpoint='markdown',
            view_func=lambda: self.export_to_markdown()
        )
        blueprint.add_url_rule(
            rule='/',
            endpoint='index',
            view_func=lambda: render_template("index.html")
        )
        self.app.register_blueprint(blueprint)

    @property
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
