import cv2


class VisualDetection:

    def __init__(self, min_contour_area: int):
        self.backsub = cv2.createBackgroundSubtractorMOG2()
        self.min_contour_area = min_contour_area

    def process(self, frame):
        fg_mask = self.backsub.apply(frame)
        
        retval, mask_thresh = cv2.threshold(fg_mask, 180, 255, cv2.THRESH_BINARY)
    
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        mask_eroded = cv2.morphologyEx(mask_thresh, cv2.MORPH_OPEN, kernel)
    
        contours, hierarchy = cv2.findContours(mask_eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > self.min_contour_area]
    
        frame_out = frame.copy()
        for cnt in large_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            frame_out = cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 0, 200), 3)

        return frame_out
