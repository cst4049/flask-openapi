from flask import Flask
from openapi import OpenApi
from pydantic import BaseModel

app = Flask(__name__)
openapi = OpenApi(app)


class A(BaseModel):
    a: str
    b: str


class C(BaseModel):
    aa: str


class RES(BaseModel):
    code: int
    msg: str
    data: dict


@app.get('/')
@openapi.swagger()
def a(query: A):
    return 'a'


@app.route('/bb', methods=['POST'])
@openapi.swagger()
def a1(body: A):
    return body.dict()


@app.route('/cc/<string:aa>', methods=['POST'])
@openapi.swagger(responses={'200': RES})
def a2(path: C, query: A, body: C):
    print(path.dict())
    print(query.dict())
    print(body.dict())
    return {'code': 0, 'msg': '', 'data': {'a': 'b'}}


openapi.register_swagger()

app.run()
