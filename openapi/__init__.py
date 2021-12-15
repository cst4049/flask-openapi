import os
import json
from functools import wraps
from werkzeug.datastructures import MultiDict
from pydantic import ValidationError
from .models import APISpec, Components, ExternalDocumentation, Info, SecurityScheme, Tag
from flask import Blueprint, render_template, request, make_response
from .until import parse_func_info, bind_rule_swagger, validate_response, get_operation, add_swagger_info


def _do_wrapper(func, path=None, query=None, form=None, body=None, responses=None, **kwargs):
    kwargs_ = dict()
    try:
        if path:
            path_ = path(**kwargs)
            kwargs_.update({"path": path_})
        if query:
            args = request.args or MultiDict()
            args_dict = {}
            for k, v in query.schema().get('properties', {}).items():
                if k not in args:
                    continue
                if v.get('type') == 'array':
                    args_dict[k] = args.getlist(k)
                else:
                    args_dict[k] = args.get(k)
            query_ = query(**args_dict)
            kwargs_.update({"query": query_})
        if form:
            req_form = request.form or MultiDict()
            form_dict = {}
            for k, v in form.schema().get('properties', {}).items():
                if k not in req_form:
                    continue
                if v.get('type') == 'array':
                    form_dict[k] = req_form.getlist(k)
                else:
                    form_dict[k] = req_form.get(k)
            form_dict.update(**request.files.to_dict())
            form_ = form(**form_dict)
            kwargs_.update({"form": form_})
        if body:
            body_ = body(
                **request.get_json(silent=True) if request.get_json(silent=True) is not None else {})
            kwargs_.update({"body": body_})
    except ValidationError as e:
        resp = make_response(e.json(), 422)
        resp.headers['Content-Type'] = 'application/json'
        return resp

    resp = func(**kwargs_)

    if responses:
        validate_response(resp, responses)

    return resp


class OpenApi:
    def __init__(self, app, api_name='openapi', secutity=None):
        self.app = app
        self.tags = []
        self.api_name = api_name
        self.openapi_version = '3.0.3'
        self.info = Info(title='OpenAPI', version='1.0.0')
        self.api_doc_url = f'/{self.api_name}.json'
        self.components = Components()
        self.components_schemas = {}
        self.externalDocs = ExternalDocumentation(
            url=f'/{self.api_name}/markdown',
            description='Export to markdown')
        self.paths = dict()
        self.securitySchemes = secutity
        self.docExpansion = 'list'
        self.oauth_config = dict()
        self.register_swagger_html()

    def register_swagger_html(self):
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
        self.components.securitySchemes = self.securitySchemes
        spec.components = self.components
        return json.loads(spec.json(by_alias=True, exclude_none=True))

    def swagger(self, tags=None, responses=None, security=None):
        def decorate(func):
            func._swagger = True
            operation = get_operation(func)
            if security or self.securitySchemes:
                operation.security = security if security else [self.securitySchemes]
            query, body, path, form = parse_func_info(func, self.components_schemas, operation)
            add_swagger_info(self.components_schemas, responses, tags, operation)

            @wraps(func)
            def wrap(**kwargs):
                return _do_wrapper(func, query=query, body=body, path=path, form=form, **kwargs)

            return wrap
        return decorate

    def register_swagger(self):
        """注册 swagger 路径与函数信息绑定"""
        bind_rule_swagger(self.app.url_map, self.app.view_functions, self.paths)
