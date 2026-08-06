import cv2

MIN_CONTOUR_AREA = 300

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

    large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > MIN_CONTOUR_AREA]

    frame_out = frame.copy()
    for cnt in large_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        frame_out = cv2.rectangle(frame, (x,y), (x+w, y+w), (0, 0, 200), 3)

    #frame_ct = cv2.drawContours(frame, large_contours, -1, (0, 255,0), 2)

    cv2.imshow('frame', frame_out)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
