from flask import Flask
from open_api import OpenApi
from pydantic import BaseModel

app = Flask(__name__)
openapi = OpenApi(app)


class A(BaseModel):
    a: str
    b: str


@app.get('/')
@openapi.swagger
def a(query: A):
    return 'a'


openapi.register_swagger()

app.run()
