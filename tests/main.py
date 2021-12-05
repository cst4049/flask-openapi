from flask import Flask
from open_api import OpenApi
from pydantic import BaseModel

app = Flask(__name__)
openapi = OpenApi(app)


class A(BaseModel):
    a: str
    b: str


class C(BaseModel):
    aa: str


@app.get('/')
@openapi.swagger
def a(query: A):
    return 'a'


@app.route('/bb', methods=['POST'])
@openapi.swagger
def a1(body: A):
    return body.dict()


@app.route('/cc/<string:aa>', methods=['POST'])
@openapi.swagger
def a2(path: C, query: A, body: C):
    print(path.dict())
    print(query.dict())
    print(body.dict())
    return 'aaa'


openapi.register_swagger()

app.run()
