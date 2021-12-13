from flask import Flask
from openapi import OpenApi, Tag
from pydantic import BaseModel
from openapi.validator import FileStorage

app = Flask(__name__)
openapi = OpenApi(app)


tag1 = Tag(name='接口1')


class A(BaseModel):
    a: str
    b: str


class C(BaseModel):
    aa: str


class D(BaseModel):
    aab: str
    dd: FileStorage


class RES(BaseModel):
    code: int
    msg: str
    data: dict


@app.get('/')
@openapi.swagger(tags=[tag1])
def a(query: A):
    return 'a'


@app.route('/bb', methods=['POST'])
@openapi.swagger()
def a1(body: A):
    return body.dict()


@app.route('/cc/<string:aa>', methods=['POST'])
@openapi.swagger(responses={'200': RES}, tags=[tag1])
def a2(path: C, query: A, body: C):
    print(path.dict())
    print(query.dict())
    print(body.dict())
    return {'code': 0, 'msg': '', 'data': {'a': 'b'}}


@app.route('/dd', methods=['POST'])
@openapi.swagger(tags=[tag1])
def d(form: D):
    print(form.dict())
    return {'code': 0, 'msg': '', 'data': {'a': 'b'}}


openapi.register_swagger()

app.run()
