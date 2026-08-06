import cv2


camera = cv2.VideoCapture(0)
backsub = cv2.createBackgroundSubtractorMOG2()

if not camera.isOpened():
    print("Error: Cannot find Camera")

while camera.isOpened():
    ret, frame = camera.read()
    if not ret:
        break

    fg_mask = backsub.apply(frame)

    retval, mask_thresh = cv2.threshold(fg_mask, 180, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    mask_eroded = cv2.morphologyEx(mask_thresh, cv2.MORPH_OPEN, kernel)

    contours, hierarchy = cv2.findContours(mask_eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    frame_ct = cv2.drawContours(frame, contours, -1, (0, 255,0), 2)

    cv2.imshow('frame', frame_ct)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
