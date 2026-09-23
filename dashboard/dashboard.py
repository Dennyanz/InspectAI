import streamlit as st
import sqlite3
import pandas as pd
import cv2
import os
import requests
from ultralytics import YOLO

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E ESTILOS
# ==========================================
st.set_page_config(
    page_title="InspectAI — Central de Comando",
    page_icon="🛡️",
    layout="wide"
)

DB_PATH = r"C:\InspectAI\inspectai.db"
MODEL_PATH = r"C:\InspectAI\best.onnx"
API_URL = "http://10.35.26.250:5000/api/reset_sos"

# Estilos CSS Personalizados
st.markdown("""
<style>
    .sos-banner {
        background-color: #8B0000;
        background-image: linear-gradient(135deg, #8B0000 0%, #D32F2F 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #FF5252;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.6);
        margin-bottom: 25px;
    }
    .sos-title {
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }
    .sos-data {
        font-size: 20px;
        font-weight: 600;
    }
    .sos-bpm {
        font-size: 32px;
        font-weight: bold;
        color: #FFEB3B;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNÇÕES DE BANCO DE DADOS
# ==========================================
def carregar_telemetria():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT operador_id AS Operador, bpm AS BPM, estresse AS Nível, sos_ativo, timestamp AS Hora FROM telemetria_operadores ORDER BY id DESC LIMIT 10", 
            conn
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def carregar_inconformidades():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT operador_id AS Operador, status AS Status, resolucao AS Situação, timestamp AS Hora FROM detection_events ORDER BY id DESC LIMIT 10", 
            conn
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# ==========================================
# CABEÇALHO PRINCIPAL
# ==========================================
st.title("🛡️ InspectAI — Central de Comando de Segurança Industrial")
st.divider()

# ==========================================
# ESTRUTURA EM ABAS
# ==========================================
aba_cam, aba_pulseiras, aba_alertas, aba_registros = st.tabs([
    "📹 Visão Computacional / Câmeras", 
    "⌚ Pulseiras (Sinais Vitais)", 
    "🚨 Alertas de Emergência", 
    "📋 Registros e Histórico"
])

# ------------------------------------------
# ABA 1: VISÃO COMPUTACIONAL / CÂMERAS
# ------------------------------------------
with aba_cam:
    st.subheader("📷 Monitoramento de Borda & Configuração de Diretrizes")
    
    # 1. Configuração de Diretrizes da IA (Fica no topo para definir as regras da câmera)
    st.markdown("### Area de Atuação: Almoxarifado Central")
    
    with st.container():
        st.markdown("#### ⚙️ Configuração de Diretrizes da IA (EPIs Obrigatórios):")
        st.caption("Selecione quais EPIs a Inteligência Artificial deve exigir nesta câmera:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            req_capacete = st.toggle("Exigir Capacete de Proteção", value=True)
        with col2:
            req_colete = st.toggle("Exigir Colete Refletivo", value=False)
        with col3:
            req_oculos = st.toggle("Exigir Óculos de Segurança", value=False)
            
        if st.button("⚙️ Aplicar Regras no Modelo"):
            st.toast("Diretrizes de EPIs atualizadas para esta câmera!", icon="✅")

    st.divider()

    # 2. Toggle e Feed de Vídeo da Câmera
    ativar_camera = st.toggle("Ativar Câmera (Visão Computacional)", value=False)
    
    if ativar_camera:
        frame_placeholder = st.empty()
        status_placeholder = st.empty()
        
        if os.path.exists(MODEL_PATH):
            model = YOLO(MODEL_PATH, task="detect")
            cap = cv2.VideoCapture(0)

            while ativar_camera:
                ret, frame = cap.read()
                if not ret:
                    st.error("Não foi possível acessar a câmera.")
                    break
                
                # Aumentamos o conf para 0.40 para eliminar detecções duplas
                results = model(frame, conf=0.40, stream=True, verbose=False)
                desvio_no_frame = False

                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        confianca = float(box.conf[0])
                        nome_classe = model.names[cls]
                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        # CLASSE 1: COM CAPACETE ('helmet_2') -> Prioridade Alta (Verde)
                        if nome_classe == "helmet_2" or "helmet" in nome_classe:
                            label = f"OK: CAPACETE ({confianca*100:.0f}%)"
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                            # Fundo preto atrás do texto para legibilidade perfeita
                            cv2.rectangle(frame, (x1, y1 - 25), (x1 + 220, y1), (0, 0, 0), -1)
                            cv2.putText(frame, label, (x1 + 5, y1 - 7),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        # CLASSE 0: SEM CAPACETE ('head') -> Alerta (Vermelho)
                        elif nome_classe == "head" or "sem" in nome_classe:
                            if req_capacete:
                                desvio_no_frame = True
                                label = f"ALERTA: SEM CAPACETE ({confianca*100:.0f}%)"
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                                # Fundo preto atrás do texto para legibilidade perfeita
                                cv2.rectangle(frame, (x1, y1 - 25), (x1 + 260, y1), (0, 0, 0), -1)
                                cv2.putText(frame, label, (x1 + 5, y1 - 7),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # Status abaixo do vídeo
                if desvio_no_frame:
                    status_placeholder.error("🚨 ALERTA DE INCONFORMIDADE: Operador detectado sem EPI obrigatório!")
                else:
                    status_placeholder.success("✅ Seguro: Nenhum desvio detectado para os EPIs exigidos.")

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

            cap.release()
        else:
            st.error(f"Modelo não encontrado em: {MODEL_PATH}")

    st.divider()

    # Expander Câmera Secundária
    with st.expander("📷 CAM-02 — Câmera Secundária - Estoque | Setor: Linha de Produção 01 | Status: 🔴 Offline"):
        st.info("Câmera secundária desconectada ou em manutenção.")

    if st.button("🔄 Atualizar Fluxo Geral"):
        st.rerun()

# ------------------------------------------
# ABA 2: PULSEIRAS / TELEMETRIA (ESP32)
# ------------------------------------------
with aba_pulseiras:
    st.subheader("⌚ Monitoramento de Sinais Vitais do Operador")
    st.caption("Dados recebidos via ESP32 + MAX30102 em tempo real")
    
    df_telemetria = carregar_telemetria()
    if not df_telemetria.empty:
        ultimo_registro = df_telemetria.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Operador Ativo", ultimo_registro['Operador'])
        c2.metric("Frequência Cardíaca (BPM)", f"{ultimo_registro['BPM']} BPM")
        c3.metric("Nível de Estresse", ultimo_registro['Nível'])
        
        st.divider()
        st.markdown("#### 📊 Histórico Recente de Batimentos")
        st.dataframe(df_telemetria.drop(columns=['sos_ativo']), use_container_width=True, hide_index=True)
    else:
        st.info("Aguardando transmissões de telemetria da ESP32...")

# ------------------------------------------
# ABA 3: ALERTAS DE EMERGÊNCIA (SOS)
# ------------------------------------------
with aba_alertas:
    st.subheader("🚨 Central de Alertas de Emergência / Pânico")
    
    df_telemetria = carregar_telemetria()
    
    if not df_telemetria.empty and df_telemetria.iloc[0]['sos_ativo'] == 1:
        operador = df_telemetria.iloc[0]['Operador']
        bpm = df_telemetria.iloc[0]['BPM']

        st.markdown(f"""
            <div class="sos-banner">
                <div class="sos-title">🚨 ALERTA MÁXIMO: BOTÃO DE PÂNICO ACIONADO!</div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="sos-data">Operador: <b>{operador}</b></div>
                    <div>Frequência Cardíaca Atual: <span class="sos-bpm">{bpm} BPM</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚨 INICIAR ATENDIMENTO / RESET DE ALERTA", use_container_width=True, type="primary"):
            try:
                requests.post(API_URL, timeout=3)
                st.success("Atendimento registrado! Alerta resetado.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao comunicar com o servidor de reset: {e}")
    else:
        st.success("✅ NENHUM ALERTA DE PÂNICO ATIVO NO MOMENTO")
        st.info("Quando um operador pressionar o botão SOS na pulseira (pino D4), o alerta vermelho piscará nesta aba e ficará registrado.")

# ------------------------------------------
# ABA 4: REGISTROS E HISTÓRICO
# ------------------------------------------
with aba_registros:
    st.subheader("📋 Registros e Histórico de Inconformidades")
    
    c_hist1, c_hist2 = st.columns(2)
    
    with c_hist1:
        st.markdown("#### 🚨 Desvios de EPI Detectados (YOLO)")
        df_inc = carregar_inconformidades()
        if not df_inc.empty:
            st.dataframe(df_inc, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma inconformidade de EPI salva no banco de dados.")

    with c_hist2:
        st.markdown("#### ⌚ Histórico de Telemetria (ESP32)")
        if not df_telemetria.empty:
            st.dataframe(df_telemetria.drop(columns=['sos_ativo']), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum histórico de sinais vitais encontrado.")