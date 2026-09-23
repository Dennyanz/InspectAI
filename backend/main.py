import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

# Mapeia o caminho correto do banco de dados na raiz do projeto
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "inspectai.db")

class AlertaEPI(BaseModel):
    status: str
    operador_id: str
    bpm: int

class AutoCorrecao(BaseModel):
    operador_id: str
    resolucao: str

@app.post("/enviar_vital")
async def enviar_vital(dados: AlertaEPI):
    # Recebe o alerta da IA e salva na tabela 'alerts'
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alerts (operador_id, status, resolucao) VALUES (?, ?, ?)",
            (dados.operador_id, dados.status, "Pendente")
        )
        conn.commit()
        conn.close()
        return {"status": "sucesso", "mensagem": "Alerta salvo com sucesso!"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.post("/autocorrigir")
async def autocorrigir_alerta(dados: AutoCorrecao):
    # Atualiza o status quando o operador coloca o EPI de volta
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE alerts SET resolucao = ? WHERE operador_id = ? AND resolucao = 'Pendente'",
            (dados.resolucao, dados.operador_id)
        )
        conn.commit()
        conn.close()
        return {"status": "sucesso"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)