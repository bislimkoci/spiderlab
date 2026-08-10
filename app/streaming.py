from __future__ import annotations

import cv2

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


def mjpeg_stream(camera_worker, settings: StreamSettings):
    last_frame_number = 0
    while True:
        last_frame_number, image_bytes = camera_worker.get_latest_encoded_jpeg(
            last_frame_number
        )
        if image_bytes is None:
            break
        yield mjpeg_frame(image_bytes, settings.boundary)
