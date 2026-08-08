import cv2

from app.camera import Camera, CameraError
from app.config import settings
from app.processing import VisualDetection


def main() -> None:
    camera = Camera(settings.camera)
    processing = VisualDetection(settings.detection)

    try:
        camera.open()
        while True:
            frame = camera.read()
            frame_out = processing.process(frame)

            cv2.imshow("frame", frame_out)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except CameraError as exc:
        print(f"Camera error: {exc}")
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
