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
class StreamSettings:
    jpeg_quality: int = 85
    boundary: str = "frame"


@dataclass(frozen=True)
class Settings:
    camera: CameraSettings = CameraSettings()
    detection: DetectionSettings = DetectionSettings()
    stream: StreamSettings = StreamSettings()


settings = Settings()
