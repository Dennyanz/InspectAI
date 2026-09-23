from pydantic import BaseModel, Field
from typing import Optional

class WearableTelemetry(BaseModel):
    wearable_id: str
    heart_rate: int
    spo2: int
    temperature: float
    battery: int
    fall_detection: bool
    sos: bool

class CameraDetectionEvent(BaseModel):
    camera_id: str
    timestamp: str
    person_detected: bool
    helmet: bool
    vest: bool
    goggles: bool
    risk_level: str
    event: str