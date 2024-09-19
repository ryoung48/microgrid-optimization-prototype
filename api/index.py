from fastapi import FastAPI
from api.test_fun import run

app = FastAPI()

@app.get("/api/python")
def hello_world():
    return {"message": "Hello World", "python": run()}