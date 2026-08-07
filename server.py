from fastapi import FastAPI
import cv2
from fastapi.responses import StreamingResponse


app = FastAPI()

def video_stream():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/video")
async def streaming_endpoint():
    return StreamingResponse(video_stream(), media_type='multipart/x-mixed-replace; boundary=frame')


