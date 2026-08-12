from __future__ import annotations

import cv2

from ultralytics import YOLO
from app.config import DetectionSettings, PeopleDetectionSettings


class VisualDetection:
    def __init__(self, settings: DetectionSettings):
        self.settings = settings
        self._background_subtractor = cv2.createBackgroundSubtractorMOG2()
        self._kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            self.settings.morph_kernel_size,
        )

    def process(self, frame):
        mask = self.motion_mask(frame)
        contours = self.large_contours(mask)
        return self.draw_detections(frame, contours)

    def motion_mask(self, frame):
        foreground = self._background_subtractor.apply(frame)
        _, thresholded = cv2.threshold(
            foreground,
            self.settings.threshold,
            255,
            cv2.THRESH_BINARY,
        )
        return cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, self._kernel)

    def large_contours(self, mask):
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        return [
            contour
            for contour in contours
            if cv2.contourArea(contour) > self.settings.min_contour_area
        ]

    def draw_detections(self, frame, contours):
        output = frame.copy()
        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)
            cv2.rectangle(
                output,
                (x, y),
                (x + width, y + height),
                (0, 0, 200),
                3,
            )
        return output


class PeopleDetection:
    def __init__(self, settings: PeopleDetectionSettings):
        self.settings = settings
        self._model = YOLO(self.settings.model_path)

    def process(self, frame):
        return self.draw_detections(frame, self.detect(frame))

    def detect(self, frame):
        results = self._model.predict(
            source=frame,
            classes=[self.settings.person_class_id],
            conf=self.settings.confidence,
            verbose=False,
        )
        if not results:
            return []

        boxes = getattr(results[0], "boxes", None)
        if boxes is None:
            return []

        detections = []
        for box in boxes:
            detections.append(self._square_bounds(box.xyxy[0].tolist(), frame.shape[:2]))

        return detections

    def draw_detections(self, frame, detections):
        output = frame.copy()
        for x1, y1, x2, y2 in detections:
            cv2.rectangle(
                output,
                (x1, y1),
                (x2, y2),
                self.settings.box_color,
                self.settings.box_thickness,
            )

        return output

    def _square_bounds(self, xyxy, frame_shape):
        frame_height, frame_width = frame_shape
        x1, y1, x2, y2 = (int(round(value)) for value in xyxy)
        box_width = max(1, x2 - x1)
        box_height = max(1, y2 - y1)
        side = min(max(box_width, box_height), frame_width - 1, frame_height - 1)

        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        square_x1 = center_x - side // 2
        square_y1 = center_y - side // 2

        square_x1 = max(0, min(square_x1, frame_width - side - 1))
        square_y1 = max(0, min(square_y1, frame_height - side - 1))

        return (
            square_x1,
            square_y1,
            square_x1 + side,
            square_y1 + side,
        )
