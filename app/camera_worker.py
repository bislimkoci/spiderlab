import threading
import time
from collections import deque
from threading import Condition

from app.camera import Camera, CameraError
from app.config import StreamSettings
from app.config import Settings
from app.process_worker import ProcessWorker

from app.streaming import encode_jpeg


class CameraWorker(threading.Thread):


    def __init__(self, camera: Camera, processor, settings: Settings):
        super().__init__(daemon=True)
        self.camera : Camera = camera
        self.settings : Settings = settings
        self.process_worker = ProcessWorker(processor, self.settings.process_worker)
        self._condition = Condition()
        self._stop_event = threading.Event()
        self._frame_number = 0
        self._frame_times = deque(maxlen=90)
        self.H : float | None = None
        self.latest_encoded_jpeg : bytes | None = None


    def run(self):
        if self.H is None:
            self.H = 1 / self.settings.camera_worker.fps

        stream_settings : StreamSettings = self.settings.stream
        process_worker_started = False

        try:
            self.process_worker.start()
            process_worker_started = True
            while not self._stop_event.is_set():
                start : float = time.perf_counter()

                frame = self.camera.read()
                self.process_worker.submit(frame)
                processed_frame = self.process_worker.latest_frame(frame)
                encoded_frame = encode_jpeg(processed_frame, stream_settings)
                with self._condition:
                    self.latest_encoded_jpeg = encoded_frame
                    self._frame_number += 1
                    self._frame_times.append(time.perf_counter())
                    self._condition.notify_all()

                execution_time : float = time.perf_counter() - start
                remaining_time : float = self.H - execution_time

                if remaining_time > 0:
                    self._stop_event.wait(remaining_time)
        except CameraError:
            pass
        finally:
            self.process_worker.stop()
            if process_worker_started:
                self.process_worker.join()
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

    def get_stats(self) -> dict:
        with self._condition:
            frame_times = list(self._frame_times)
            fps = 0.0
            if len(frame_times) >= 2:
                elapsed = frame_times[-1] - frame_times[0]
                if elapsed > 0:
                    fps = (len(frame_times) - 1) / elapsed

            return {
                "running": self.is_alive() and not self._stop_event.is_set(),
                "frames": self._frame_number,
                "fps": round(fps, 1),
                "target_fps": self.settings.camera_worker.fps,
                "has_frame": self.latest_encoded_jpeg is not None,
                "processor": self.process_worker.get_stats(),
            }
