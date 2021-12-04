```
from flask import Flask
from flask-swagger import Openapi
from pydantic import BaseModel

class Q(BaseModel):
    a: str
    b: str

app = Flask(__name__)
openapi = Openapi(app)

@app.route('/')
@openapi.swagger
def r1(query: Q):
    return ''

openapi.register_swagger()

app.run()
```