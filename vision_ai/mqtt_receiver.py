import json
import datetime
import paho.mqtt.client as mqtt
from database import inicializar_banco, atualizar_telemetria

MQTT_BROKER = "127.0.0.1"
TOPICO_TELEMETRIA = "inspectai/pulseira/telemetria"

def on_message(client, userdata, msg):
    try:
        dados = json.loads(msg.payload.decode())
        agora = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Envia para as funções do banco de dados
        atualizar_telemetria(
            id_pulseira=dados.get("id_pulseira", "WP-01"),
            operador=dados.get("operador", "Denilson Borba"),
            bpm=dados.get("bpm", 0),
            temperatura=dados.get("temperatura", 0.0),
            bateria=dados.get("bateria", 100),
            sos=dados.get("sos", False),
            area=dados.get("area", "Montagem de Estruturas Pesadas"),
            timestamp_atual=agora
        )
        print(f"📥 Dados de saúde salvos para o operador: {dados.get('operador')}")
    except Exception as e:
        print(f"Erro no processamento dos dados MQTT: {e}")

if __name__ == "__main__":
    # Força a criação das tabelas antes de ligar o MQTT
    inicializar_banco()
    
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.subscribe(TOPICO_TELEMETRIA)
    
    print("⌚ Receptor MQTT da Pulseira Ativo e tabelas verificadas!")
    client.loop_forever()