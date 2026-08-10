from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.camera import Camera
from app.camera_worker import CameraWorker
from app.config import settings
from app.processing import VisualDetection
from app.streaming import mjpeg_stream


camera = Camera(settings.camera)
processor = VisualDetection(settings.detection)
camera_worker = CameraWorker(camera, processor, settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    camera.open()
    camera_worker.start()
    try:
        yield
    finally:
        camera_worker.stop()
        camera_worker.join()
        camera.release()


app = FastAPI(lifespan=lifespan)


@app.get("/video")
def video():
    return StreamingResponse(
        mjpeg_stream(camera_worker, settings.stream),
        media_type=f"multipart/x-mixed-replace; boundary={settings.stream.boundary}",
    )
