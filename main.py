import cv2
import numpy as np

from app.camera import Camera, CameraError
from app.camera_worker import CameraWorker
from app.config import settings
from app.processing import VisualDetection


def decode_jpeg(image_bytes: bytes):
    image_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(image_buffer, cv2.IMREAD_COLOR)
    if frame is None:
        raise RuntimeError("Could not decode JPEG frame")
    return frame


def main() -> None:
    camera = Camera(settings.camera)
    processor = VisualDetection(settings.detection)
    camera_worker = CameraWorker(camera, processor, settings)
    worker_started = False
    last_frame_number = 0

    try:
        camera.open()
        camera_worker.start()
        worker_started = True

        while True:
            last_frame_number, image_bytes = camera_worker.get_latest_encoded_jpeg(
                last_frame_number
            )
            if image_bytes is None:
                break

            cv2.imshow("frame", decode_jpeg(image_bytes))

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except CameraError as exc:
        print(f"Camera error: {exc}")
    finally:
        camera_worker.stop()
        if worker_started:
            camera_worker.join()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
