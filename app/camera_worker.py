import threading
import time
from threading import Condition

from app.camera import Camera, CameraError
from app.config import StreamSettings
from app.config import Settings

from app.streaming import encode_jpeg


class CameraWorker(threading.Thread):


    def __init__(self, camera: Camera, processor, settings: Settings):
        super().__init__(daemon=True)
        self.camera : Camera = camera
        self.processor = processor
        self.settings : Settings = settings
        self._condition = Condition()
        self._stop_event = threading.Event()
        self._frame_number = 0
        self.H : float | None = None
        self.latest_encoded_jpeg : bytes | None = None


    def run(self):
        if self.H is None:
            self.H = 1 / self.settings.camera_worker.fps

        stream_settings : StreamSettings = self.settings.stream

        try:
            while not self._stop_event.is_set():
                start : float = time.perf_counter()

                frame = self.camera.read()
                processed_frame = self.processor.process(frame)
                encoded_frame = encode_jpeg(processed_frame, stream_settings)
                with self._condition:
                    self.latest_encoded_jpeg = encoded_frame
                    self._frame_number += 1
                    self._condition.notify_all()

                execution_time : float = time.perf_counter() - start
                remaining_time : float = self.H - execution_time

                if remaining_time > 0:
                    self._stop_event.wait(remaining_time)
        except CameraError:
            pass
        finally:
            self.stop()

    def stop(self) -> None:
        self._stop_event.set()
        with self._condition:
            self._condition.notify_all()

    def get_latest_encoded_jpeg(self, last_frame_number: int = 0):
        with self._condition:
            self._condition.wait_for(
                lambda: self._frame_number > last_frame_number or self._stop_event.is_set()
            )
            if self._frame_number <= last_frame_number:
                return self._frame_number, None
            return self._frame_number, self.latest_encoded_jpeg
