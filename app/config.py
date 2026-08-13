from dataclasses import dataclass


@dataclass(frozen=True)
class CameraSettings:
    index: int = 0
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True)
class DetectionSettings:
    min_contour_area: int = 300
    threshold: int = 180
    morph_kernel_size: tuple[int, int] = (3, 3)


@dataclass(frozen=True)
class PeopleDetectionSettings:
    model_path: str = "yolov8n.pt"
    confidence: float = 0.4
    person_class_id: int = 0
    box_color: tuple[int, int, int] = (0, 0, 255)
    box_thickness: int = 3


@dataclass(frozen=True)
class StreamSettings:
    jpeg_quality: int = 85
    boundary: str = "frame"

@dataclass(frozen=True)
class CameraWorkerSettings:
    fps : int = 15


@dataclass(frozen=True)
class ProcessWorkerSettings:
    fps: int = 1
    notification_on : bool = True


@dataclass(frozen=True)
class Settings:
    camera: CameraSettings = CameraSettings()
    detection: DetectionSettings = DetectionSettings()
    people_detection: PeopleDetectionSettings = PeopleDetectionSettings()
    stream: StreamSettings = StreamSettings()
    camera_worker : CameraWorkerSettings = CameraWorkerSettings()
    process_worker: ProcessWorkerSettings = ProcessWorkerSettings()


settings = Settings()
