from flask_openapi3 import OpenAPI
from pydantic import BaseModel


class A(BaseModel):
    a: str


class C(BaseModel):
    aa: str


app = OpenAPI(__name__)


@app.get('/')
def a(query: A):
    return ''


@app.get('/cc/<string:aa>')
def a2(path: C):
    return 'aaa'


app.run()
