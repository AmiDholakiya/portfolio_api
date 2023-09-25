from fastapi import FastAPI

app = FastAPI()

@app.get("/test",tags=["Root"])
async def read_root():
    return {"message": "Welcome!"}