from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.config.database import Base

class WorkerModel(Base):
    __tablename__ = "workers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    associated_wearable: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

class CameraModel(Base):
    __tablename__ = "cameras"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ONLINE")

class DetectionEventModel(Base):
    __tablename__ = "detection_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str] = mapped_column(String(50), index=True)
    event_type: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float)
    image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)

# VEJA SE ESTA CLASSE EXISTE EXATAMENTE COM ESSE NOME NO FINAL DO ARQUIVO:
class AlertModel(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(String(255))
    camera_id: Mapped[str] = mapped_column(String(50))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class TelemetryHistoryModel(Base):
    __tablename__ = "telemetry_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wearable_id: Mapped[str] = mapped_column(String(50), index=True)
    heart_rate: Mapped[int] = mapped_column(Integer)
    spo2: Mapped[int] = mapped_column(Integer)
    temperature: Mapped[float] = mapped_column(Float)
    battery: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))