from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "C:\\InspectAI\\inspectai.db"

def obter_conexao_banco():
    # Timeout de 5 segundos evita travamentos se a câmera e o painel acessarem juntos
    conn = sqlite3.connect(DB_PATH, timeout=5)
    return conn

# ==========================================
# 1. ENDPOINTS DO PAINEL DE ALERTAS (IA)
# ==========================================

@app.route('/api/incidentes/ativos', methods=['GET'])
def obter_incidentes_ativos():
    """Retorna apenas os últimos 30 incidentes pendentes para não travar o painel"""
    try:
        conn = obter_conexao_banco()
        cursor = conn.cursor()
        
        # Seleciona apenas os que não foram resolvidos ainda
        cursor.execute('''
            SELECT id, operador_id, status, resolucao 
            FROM detection_events 
            WHERE status = 'INCONFORMIDADE' AND resolucao = 'Pendente'
            ORDER BY id DESC 
            LIMIT 30
        ''')
        
        colunas = [col[0] for col in cursor.description]
        incidentes = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
        
        conn.close()
        return jsonify(incidentes), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


@app.route('/api/incidentes/resolver/<int:id_incidente>', methods=['POST'])
def resolver_incidente(id_incidente):
    """Muda o status do incidente para 'Resolvido', limpando-o do painel ativo"""
    try:
        conn = obter_conexao_banco()
        cursor = conn.cursor()
        
        # Verifica se o incidente existe
        cursor.execute("SELECT id FROM detection_events WHERE id = ?", (id_incidente,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"status": "erro", "mensagem": "Incidente nao encontrado."}), 404
            
        # Atualiza a resolução
        cursor.execute('''
            UPDATE detection_events 
            SET resolucao = 'Resolvido' 
            WHERE id = ?
        ''', (id_incidente,))
        
        conn.commit()
        conn.close()
        return jsonify({"status": "sucesso", "mensagem": f"Incidente #{id_incidente} resolvido com sucesso."}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


# ==========================================
# 2. ENDPOINT DE TELEMETRIA DA PULSEIRA (IoT)
# ==========================================

@app.route('/api/telemetria', methods=['POST'])
def receber_telemetria():
    """Recebe e valida os dados de sinais vitais vindos do ESP32"""
    dados = request.get_json()
    
    if not dados:
        return jsonify({"status": "erro", "mensagem": "Dados nao fornecidos"}), 400
        
    operador_id = dados.get('operador_id')
    frequencia_cardiaca = dados.get('frequencia_cardiaca')
    temperatura = dados.get('temperatura')
    
    # VALIDAÇÃO: Evita gravação de ruídos ou dados nulos no banco
    if not operador_id or frequencia_cardiaca is None or temperatura is None:
        return jsonify({"status": "erro", "mensagem": "Campos obrigatorios ausentes ou nulos."}), 400
        
    # Filtro de segurança para leituras absurdas do sensor
    if frequencia_cardiaca < 30 or frequencia_cardiaca > 220 or temperatura < 30 or temperatura > 45:
        return jsonify({"status": "erro", "mensagem": "Leitura descartada por incoerencia dos sensores."}), 400

    try:
        conn = obter_conexao_banco()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO telemetry_history (operador_id, freq_cardiaca, temperatura, timestamp)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
        ''', (operador_id, frequencia_cardiaca, temperatura))
        
        conn.commit()
        conn.close()
        return jsonify({"status": "sucesso", "mensagem": "Telemetria gravada."}), 201
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    print("🌐 Servidor Backend InspectAI rodando na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)