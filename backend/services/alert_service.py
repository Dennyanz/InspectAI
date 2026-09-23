import logging
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.orm_models import AlertModel
from paho.mqtt import client as mqtt

logger = logging.getLogger("InspectAI.AlertService")

class AlertService:
    def __init__(self, broker: str = "127.0.0.1", port: int = 1883) -> None:
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        try:
            self.mqtt_client.connect(broker, port, keepalive=60)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"[MQTT ALERT] Falha ao acoplar barramento MQTT: {e}")

    async def generate_alert(self, db: AsyncSession, alert_type: str, priority: str, description: str, camera_id: str) -> None:
        logger.warning(f"[ALERTA ATIVO] Tipo: {alert_type} | Severidade: {priority} | {description}")
        
        # Persistência em Banco
        db_alert = AlertModel(type=alert_type, priority=priority, description=description, camera_id=camera_id)
        db.add(db_alert)
        await db.commit()

        # Publicação via Barramento MQTT
        payload = {"type": alert_type, "priority": priority, "description": description, "camera": camera_id}
        self.mqtt_client.publish("smartsafe/vision/alerts", payload=str(payload), qos=1)