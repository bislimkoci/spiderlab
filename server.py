from fastapi import FastAPI
import cv2


app = FastAPI()

@app.get("/hello")
async def hello():
    return "Hello"