
import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from app.camera import Camera
from app.processing import VisualDetection

app = FastAPI()

camera = Camera()
processing = VisualDetection(300)

def video_stream():
    while True:
        frame = camera.take_pic()
        processed_frame = processing.process(frame)
        _, buffer = cv2.imencode('.jpg', processed_frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/video")
def video():
    return StreamingResponse(
        video_stream(), 
        media_type='multipart/x-mixed-replace; boundary=frame'
    )