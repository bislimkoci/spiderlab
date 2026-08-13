import threading
import time
from collections import deque
from threading import Condition

from app.config import ProcessWorkerSettings


class ProcessWorker(threading.Thread):
    def __init__(self, processor, settings: ProcessWorkerSettings):
        super().__init__(daemon=True)
        self.processor = processor
        self.settings = settings
        self._condition = Condition()
        self._stop_event = threading.Event()
        self._input_frame = None
        self._input_sequence = 0
        self._processed_frame = None
        self._detections = None
        self._process_count = 0
        self._process_times = deque(maxlen=30)
        self._last_error: str | None = None
        self._person_detected_last_frame = False
        self._notification_count = 0
        self._last_notification_error: str | None = None
        self._detect = getattr(self.processor, "detect", None)
        self._draw_detections = getattr(self.processor, "draw_detections", None)

    def submit(self, frame) -> None:
        with self._condition:
            self._input_frame = frame
            self._input_sequence += 1
            self._condition.notify()

    def latest_frame(self, fallback_frame):
        with self._condition:
            detections = self._detections
            processed_frame = self._processed_frame

        if detections is not None and self._draw_detections is not None:
            return self._draw_detections(fallback_frame, detections)
        if processed_frame is not None:
            return processed_frame
        return fallback_frame

    def run(self) -> None:
        interval = 1 / self.settings.fps
        last_started_at = 0.0
        last_sequence = 0

        while not self._stop_event.is_set():
            with self._condition:
                self._condition.wait_for(
                    lambda: (
                        self._input_sequence > last_sequence
                        or self._stop_event.is_set()
                    )
                )
                if self._stop_event.is_set():
                    break

            wait_time = interval - (time.perf_counter() - last_started_at)
            if wait_time > 0 and self._stop_event.wait(wait_time):
                break

            with self._condition:
                frame = self._input_frame
                sequence = self._input_sequence

            if frame is None:
                continue

            last_started_at = time.perf_counter()
            result_kind = "frame"
            try:
                if self._detect is not None and self._draw_detections is not None:
                    processed_result = self._detect(frame)
                    result_kind = "detections"
                else:
                    processed_result = self.processor.process(frame)
            except Exception as exc:
                processed_result = None
                with self._condition:
                    self._last_error = str(exc)

            should_send_notification = False
            with self._condition:
                last_sequence = sequence
                if processed_result is not None:
                    if result_kind == "detections":
                        self._detections = processed_result
                        self._processed_frame = None
                        person_detected = bool(processed_result)
                        should_send_notification = (
                            person_detected
                            and not self._person_detected_last_frame
                        )
                        self._person_detected_last_frame = person_detected
                    else:
                        self._processed_frame = processed_result
                        self._detections = None
                    self._process_count += 1
                    self._process_times.append(time.perf_counter())
                    self._last_error = None
                self._condition.notify_all()

            if should_send_notification:
                self._send_detection_notification()

    def _send_detection_notification(self) -> None:
        try:
            from app.notification import send_detection_message_discord
            if self.settings.notification_on:
                send_detection_message_discord()
        except Exception as exc:
            with self._condition:
                self._last_notification_error = str(exc)
        else:
            with self._condition:
                self._notification_count += 1
                self._last_notification_error = None

    def stop(self) -> None:
        self._stop_event.set()
        with self._condition:
            self._condition.notify_all()

    def get_stats(self) -> dict:
        with self._condition:
            process_times = list(self._process_times)
            fps = 0.0
            if len(process_times) >= 2:
                elapsed = process_times[-1] - process_times[0]
                if elapsed > 0:
                    fps = (len(process_times) - 1) / elapsed

            return {
                "running": self.is_alive() and not self._stop_event.is_set(),
                "frames": self._process_count,
                "input_frames": self._input_sequence,
                "fps": round(fps, 1),
                "target_fps": self.settings.fps,
                "has_frame": (
                    self._processed_frame is not None
                    or self._detections is not None
                ),
                "last_error": self._last_error,
                "person_detected": self._person_detected_last_frame,
                "notifications": self._notification_count,
                "last_notification_error": self._last_notification_error,
            }
