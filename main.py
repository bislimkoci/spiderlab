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
    cv2.imshow('frame', fg_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
