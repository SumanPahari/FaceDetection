from fastapi import FastAPI

app = FastAPI()

@app.post("/getname")
def read_root(name:str):
    return {"message": f"Hello, World {name}"}