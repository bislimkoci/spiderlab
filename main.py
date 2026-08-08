import cv2
from app.camera import Camera
from app.processing import VisualDetection

MIN_CONTOUR_AREA = 300

camera = Camera()
processing = VisualDetection(MIN_CONTOUR_AREA)

while camera.is_open():

    frame = camera.take_pic()

    frame_out = processing.process(frame)
    
    cv2.imshow('frame', frame_out)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
