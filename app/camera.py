

import cv2


class Camera:

    def __init__(self):
        self.cap : cv2.VideoCapture = cv2.VideoCapture(0)

    def __delete__(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def take_pic(self):
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Camera not working")
        return frame

    def is_open(self) -> bool:
        return self.cap.isOpened()
            
