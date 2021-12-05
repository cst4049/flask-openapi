from flask_openapi3 import OpenAPI
from pydantic import BaseModel


class A(BaseModel):
    a: str


app = OpenAPI(__name__)


@app.get('/')
def a(query: A):
    return ''

app.run()
