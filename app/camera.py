from __future__ import annotations

from threading import Lock

import cv2

from app.config import CameraSettings


class CameraError(RuntimeError):
    """Raised when the camera cannot be opened or read."""


class Camera:
    def __init__(self, settings: CameraSettings):
        self.settings = settings
        self._capture: cv2.VideoCapture | None = None
        self._lock = Lock()

    def open(self) -> None:
        if self.is_open:
            return

        capture = cv2.VideoCapture(self.settings.index)
        if self.settings.width is not None:
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.width)
        if self.settings.height is not None:
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.height)

        if not capture.isOpened():
            capture.release()
            raise CameraError(f"Cannot open camera index {self.settings.index}")

        self._capture = capture

    def read(self):
        with self._lock:
            if not self.is_open:
                self.open()

            if self._capture is None:
                raise CameraError("Camera is not available")

            ok, frame = self._capture.read()
            if not ok or frame is None:
                raise CameraError("Could not read frame from camera")

            return frame

    def release(self) -> None:
        with self._lock:
            if self._capture is not None:
                self._capture.release()
                self._capture = None

    @property
    def is_open(self) -> bool:
        return self._capture is not None and self._capture.isOpened()
