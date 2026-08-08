from __future__ import annotations

import cv2

from app.config import DetectionSettings


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
