from __future__ import annotations

import cv2

from app.camera import Camera, CameraError
from app.config import StreamSettings


def encode_jpeg(frame, settings: StreamSettings) -> bytes:
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), settings.jpeg_quality]
    ok, buffer = cv2.imencode(".jpg", frame, encode_params)
    if not ok:
        raise RuntimeError("Could not encode frame as JPEG")
    return buffer.tobytes()


def mjpeg_frame(image_bytes: bytes, boundary: str) -> bytes:
    return (
        f"--{boundary}\r\n".encode()
        + b"Content-Type: image/jpeg\r\n\r\n"
        + image_bytes
        + b"\r\n"
    )


def mjpeg_stream(camera: Camera, processor, settings: StreamSettings):
    while True:
        try:
            frame = camera.read()
            processed_frame = processor.process(frame)
            yield mjpeg_frame(encode_jpeg(processed_frame, settings), settings.boundary)
        except CameraError:
            break
