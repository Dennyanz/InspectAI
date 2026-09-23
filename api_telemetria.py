from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = r"C:\InspectAI\inspectai.db"

def inicializar_banco():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetria_operadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operador_id TEXT,
            bpm INTEGER,
            estresse TEXT,
            sos_ativo INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.route('/api/telemetria', methods=['POST'])
def receber_telemetria():
    data = request.get_json()
    if not data:
        return jsonify({"status": "erro"}), 400

    operador_id = data.get("operador_id", "Nilson Borba")
    bpm = data.get("bpm", 0)
    sos = 1 if data.get("sos", False) else 0

    estresse = "NORMAL"
    if bpm > 100: estresse = "ALTO"
    elif bpm < 50 and bpm > 0: estresse = "BAIXO"

    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO telemetria_operadores (operador_id, bpm, estresse, sos_ativo) VALUES (?, ?, ?, ?)",
            (operador_id, bpm, estresse, sos)
        )
        conn.commit()
        conn.close()
        print(f"📡 Telemetria: {operador_id} | BPM: {bpm} | SOS: {sos}")
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

@app.route('/api/reset_sos', methods=['POST'])
def reset_sos():
    """Desativa o alerta de SOS no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()
        cursor.execute("UPDATE telemetria_operadores SET sos_ativo = 0")
        conn.commit()
        conn.close()
        return jsonify({"status": "resetado"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhe": str(e)}), 500

if __name__ == '__main__':
    inicializar_banco()
    print("==================================================")
    print("🚀 API InspectAI Ativa na Porta 5000!")
    print("📍 Endpoint: http://10.35.26.250:5000/api/telemetria")
    print("==================================================")
    app.run(host='0.0.0.0', port=5000, debug=False)