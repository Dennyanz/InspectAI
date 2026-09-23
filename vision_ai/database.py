import sqlite3

DB_NAME = "inspectai.db"

def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Cria a tabela de telemetria da pulseira
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetria (
            id_pulseira TEXT PRIMARY KEY,
            operador TEXT,
            bpm INTEGER,
            temperatura REAL,
            bateria INTEGER,
            sos INTEGER,
            area TEXT,
            timestamp TEXT
        )
    """)
    # Cria a tabela de histórico de alertas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            operador TEXT,
            area TEXT,
            tipo TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def atualizar_telemetria(id_pulseira, operador, bpm, temperatura, bateria, sos, area, timestamp_atual):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO telemetria (id_pulseira, operador, bpm, temperatura, bateria, sos, area, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (id_pulseira, operador, bpm, temperatura, bateria, int(sos), area, timestamp_atual))
    
    if sos:
        cursor.execute("""
            INSERT INTO alertas (timestamp, operador, area, tipo, status)
            VALUES (?, ?, ?, ?, 'ATIVO')
        """, (timestamp_atual, operador, area, "BOTÃO SOS PRESSIONADO"))
        
    conn.commit()
    conn.close()