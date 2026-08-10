from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.camera import Camera
from app.camera_worker import CameraWorker
from app.config import settings
from app.processing import VisualDetection
from app.streaming import mjpeg_stream
from app.system_stats import LinuxSystemStats


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DASHBOARD_FILE = BASE_DIR / "templates" / "dashboard.html"

camera = Camera(settings.camera)
processor = VisualDetection(settings.detection)
camera_worker = CameraWorker(camera, processor, settings)
system_stats = LinuxSystemStats()


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
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def dashboard():
    return FileResponse(DASHBOARD_FILE, media_type="text/html")


@app.get("/stream.mjpg")
def stream():
    return StreamingResponse(
        mjpeg_stream(camera_worker, settings.stream),
        media_type=f"multipart/x-mixed-replace; boundary={settings.stream.boundary}",
    )


@app.get("/api/stats")
def stats():
    return {
        "camera": camera_worker.get_stats(),
        "system": system_stats.snapshot(),
    }
