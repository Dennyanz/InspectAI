import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger("InspectAI.IoTService")

# CONFIGURAÇÕES DO SEU BROKER MQTT (Ajuste conforme o que colocou na pulseira)
MQTT_BROKER = "broker.hivemq.com"  # Ou o IP local do seu broker (ex: 192.168.x.x)
MQTT_PORT = 1883
MQTT_TOPIC = "inspectai/alertas"    # O tópico que a sua pulseira está escutando

def enviar_alerta_pulseira(mensagem: str):
    """
    Publica um alerta de infração no broker MQTT para acionar a pulseira.
    """
    try:
        # Inicializa o cliente MQTT
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        
        # Conecta ao servidor
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Publica a mensagem de erro (ex: "MISSING_HELMET")
        client.publish(MQTT_TOPIC, mensagem, qos=1)
        
        logger.info(f"[IoT] Alerta '{mensagem}' enviado com sucesso para o tópico '{MQTT_TOPIC}'")
        
        # Desconecta de forma limpa
        client.disconnect()
        
    except Exception as e:
        logger.error(f"[IoT] Falha ao enviar comando MQTT para a pulseira: {str(e)}")