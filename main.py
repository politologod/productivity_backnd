from fastapi import FastAPI
from routes.routes_task import router as task_router

app = FastAPI()

app.include_router(task_router)
@app.get("/")
def read_root():
    return {"message": "Welcome to the FARM API Tutorial of Fazt"}



