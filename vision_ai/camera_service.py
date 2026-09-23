import cv2
import sqlite3
import time
import os
from ultralytics import YOLO

# ==========================================
# 1. CONFIGURAÇÕES INICIAIS E CAMINHOS
# ==========================================
DB_PATH = "C:\\InspectAI\\inspectai.db"
# Carrega o modelo otimizado em formato ONNX para máxima velocidade em produção
MODEL_PATH = "C:\\InspectAI\\best.onnx" 

# Configuração do Filtro de Cooldown (Anti-Inundação de Alertas)
ultimos_alertas = {}
INTERVALO_COOLDOWN = 15  # Tempo em segundos para esperar antes de repetir um alerta

# ==========================================
# 2. INICIALIZAÇÃO DOS COMPONENTES
# ==========================================
print("🔄 Carregando modelo preditivo otimizado (YOLOv8 ONNX)...")
if not os.path.exists(MODEL_PATH):
    print(f"⚠️ Alerta: Arquivo {MODEL_PATH} nao encontrado. Verifique se realizou a exportacao.")
model = YOLO(MODEL_PATH, task="detect")

print("🔌 Inicializando captura da camera...")
cap = cv2.VideoCapture(0) # 0 para webcam padrão

if not cap.isOpened():
    print("❌ Erro: Nao foi possivel acessar a webcam.")
    exit()

print("🚀 Sistema de Visao Computacional em execucao!")

# ==========================================
# 3. LOOP DE PROCESSAMENTO EM TEMPO REAL
# ==========================================
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Falha ao capturar frame da camera.")
            break

        # Executa a inferência de IA com o modelo ONNX
        # stream=True otimiza o uso de memória RAM frame por frame
        results = model(frame, stream=True, verbose=False)

        desvio_detectado = False
        id_operario_alvo = "Operario #3" # ID simulado/detectado para o evento

        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Obtém a classe detectada (Ex: 0 = 'sem_capacete', 1 = 'sem_colete')
                cls = int(box.cls[0])
                nome_classe = model.names[cls]

                # Se a classe indicar uma infração/desvio de segurança
                if "sem" in nome_classe or "no" in nome_classe or nome_classe == "desvio":
                    desvio_detectado = True
                    
                    # Desenha a marcação visual na tela de monitoramento local
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"ALERTA: {nome_classe}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # ==========================================
        # 4. LOGICA INTELIGENTE DE GRAVAÇÃO NO BANCO
        # ==========================================
        if desvio_detectado:
            tempo_atual = time.time()
            
            # FILTRO: Verifica se o operador já gerou alerta nos últimos 15 segundos
            if id_operario_alvo not in ultimos_alertas or (tempo_atual - ultimos_alertas[id_operario_alvo]) > INTERVALO_COOLDOWN:
                try:
                    conn = sqlite3.connect(DB_PATH, timeout=5)
                    cursor = conn.cursor()
                    
                    # Grava o evento com status estrito para o painel Streamlit capturar
                    cursor.execute(
                        "INSERT INTO detection_events (operador_id, status, resolucao) VALUES (?, 'INCONFORMIDADE', 'Pendente')",
                        (id_operario_alvo,)
                    )
                    conn.commit()
                    conn.close()
                    
                    # Atualiza o cronômetro do último alerta enviado para este operador
                    ultimos_alertas[id_operario_alvo] = tempo_atual
                    print(f"🚨 [BANCO DE DADOS] Novo alerta gerado para {id_operario_alvo}. Bloqueio de 15s ativo.")
                    
                except sqlite3.OperationalError as e:
                    print(f"⚠️ Banco travado temporariamente, nova tentativa no proximo frame: {e}")

        # Exibe o feed da câmera na tela
        cv2.imshow("InspectAI - Monitoramento de Borda Industrial", frame)

        # Tecla 'q' para acessar de forma segura
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n🛑 Interrupcao manual recebida.")

finally:
    # Liberação limpa de recursos de hardware
    cap.release()
    cv2.destroyAllWindows()
    print("🏁 Servico de camera encerrado com sucesso.")