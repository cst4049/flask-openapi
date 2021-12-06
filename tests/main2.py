from flask_openapi3 import OpenAPI, Tag
from pydantic import BaseModel


tag = Tag(name='aaa')

class A(BaseModel):
    a: str


class C(BaseModel):
    aa: str


app = OpenAPI(__name__)


@app.get('/', tags=[tag])
def a(query: A):
    return ''


@app.get('/cc/<string:aa>')
def a2(path: C):
    return 'aaa'


app.run()
