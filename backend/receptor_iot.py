from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Caminho do arquivo onde o status será compartilhado com o Dashboard
STATUS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'status.json')

@app.route('/enviar_vital', methods=['POST'])
def enviar_vital():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"status": "error", "message": "JSON inválido ou ausente"}), 400
        
        # Garante os dados vindos do ESP32 ou Celular
        status_atual = dados.get('status', 'EMERGENCIA_SOS')
        operador = dados.get('operador_id', 'Denilson Borba')
        bpm = dados.get('bpm', 115)
        
        # Estrutura o pacote padrão limpo
        dados_salvar = {
            "status": status_atual,
            "operador_id": operador,
            "bpm": bpm
        }
        
        # Salva o estado atual no arquivo json para o Streamlit ler instantaneamente
        with open(STATUS_FILE, 'w') as f:
            json.dump(dados_salvar, f)
            
        print(f"\n🚨 [ALERTA PROCESSADO] {operador} -> Status: {status_atual} ({bpm} BPM) | Gravado com sucesso!")
        
        return jsonify({
            "status": "success",
            "message": "Alerta processado com sucesso!"
        }), 200

    except Exception as e:
        print(f"Erro interno no receptor: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/reset_alert', methods=['POST'])
def reset_alert():
    try:
        dados_normais = {"status": "NORMAL", "operador_id": "Nenhum", "bpm": 80}
        with open(STATUS_FILE, 'w') as f:
            json.dump(dados_normais, f)
        return jsonify({"status": "success", "message": "Alerta resetado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)