import streamlit as st
import qrcode
import json
import sqlite3
import pandas as pd
from io import BytesIO
import datetime

st.set_page_config(page_title="InspectAI - Industrial Safety Intelligence", layout="wide")

# Estilos Visuais do seu Painel Escuro
st.markdown("""
    <style>
    .stApp { background-color: #0d1b2a; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1b263b; }
    .metric-card { background-color: #1e293b; padding: 15px; border-radius: 5px; border-left: 5px solid #00b4d8; margin-bottom: 10px; }
    .alert-card { background-color: #780000; border: 2px solid #dc2f02; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM BANCO PARA ATUALIZAÇÃO EM TEMPO REAL ---
def buscar_dados():
    conn = sqlite3.connect("inspectai.db")
    df_telemetria = pd.read_sql_query("SELECT * FROM telemetria", conn)
    df_alertas = pd.read_sql_query("SELECT * FROM alertas WHERE status='ATIVO' ORDER BY id DESC", conn)
    conn.close()
    return df_telemetria, df_alertas

df_tel, df_al = buscar_dados()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("⚙️ InspectAI")
    st.caption("Industrial Safety Intelligence")
    st.markdown("---")
    st.subheader("📱 Pareamento Móvel")
    
    # Payload JSON que o seu aplicativo vai ler ao escanear
    config_app = {"server_ip": "192.168.0.105", "mqtt_port": 1883, "token": "SECURE_2026"}
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(json.dumps(config_app))
    qr.make(fit=True)
    img_buf = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(img_buf, format="PNG")
    
    st.image(img_buf, use_column_width=True)
    st.markdown("---")
    st.subheader("🔒 Status de Infraestrutura")
    st.success("● Broker MQTT")
    st.success("● Banco de Dados")
    st.success("● API REST")

# --- CONTEÚDO PRINCIPAL ---
agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
st.markdown(f"<p style='text-align: right; color: #a2d2ff;'>🕒 {agora} | V1.0.0 | SUPERVISOR: ENG. ADM</p>", unsafe_allow_html=True)

# Métricas do Topo Dinâmicas
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown(f"<div class='metric-card'><p style='color:#00b4d8; font-size:12px; margin:0;'>Operários Online</p><h2>{len(df_tel)}</h2></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='metric-card' style='border-left-color:#2a9d8f;'><p style='color:#2a9d8f; font-size:12px; margin:0;'>Pulseiras Ativas</p><h2>{len(df_tel[df_tel['bpm']>0])}</h2></div>", unsafe_allow_html=True)
with c3: st.markdown("<div class='metric-card' style='border-left-color:#e9c46a;'><p style='color:#e9c46a; font-size:12px; margin:0;'>Câmeras Online</p><h2>1</h2></div>", unsafe_allow_html=True)
with c4: st.markdown(f"<div class='metric-card' style='border-left-color:#f4a261;'><p style='color:#f4a261; font-size:12px; margin:0;'>Alertas Ativos</p><h2>{len(df_al)}</h2></div>", unsafe_allow_html=True)
with c5: st.markdown(f"<div class='metric-card' style='border-left-color:#e63946;'><p style='color:#e63946; font-size:12px; margin:0;'>Emergências</p><h2>{len(df_al[df_al['tipo']=='BOTÃO SOS PRESSIONADO'])}</h2></div>", unsafe_allow_html=True)

st.markdown("<h4 style='text-align: center; color: #a2d2ff; margin-top:20px;'>PAINEL CRÍTICO DE TRIAGEM</h4>", unsafe_allow_html=True)

# Renderiza os Cards de Emergência Crítica se houver SOS ativo no banco
for _, alerta in df_al.iterrows():
    if alerta['tipo'] == "BOTÃO SOS PRESSIONADO":
        # Busca métricas atuais do operador do SOS
        op_dados = df_tel[df_tel['operador'] == alerta['operador']]
        bpm = op_dados['bpm'].values[0] if not op_dados.empty else 0
        temp = op_dados['temperatura'].values[0] if not op_dados.empty else 0.0
        
        st.markdown(f"""
            <div class='alert-card'>
                <table style='width:100%; color:white; border:none;'>
                    <tr>
                        <td><h4 style='color:#ff4d4d; margin:0;'>🚨 EMERGÊNCIA CRÍTICA</h4><p style='font-size:12px;'>Conduta: Enviar Equipe de Resgate Médico Imediatamente.</p></td>
                        <td><p style='font-size:11px; color:#a2d2ff; margin:0;'>COLABORADOR / ÁREA</p><p style='margin:5px 0;'><b>{alerta['operador']}</b></p><p style='font-size:12px;'>{alerta['area']}</p></td>
                        <td><p style='font-size:11px; color:#a2d2ff; margin:0;'>MÉTRICAS</p><p style='margin:5px 0;'>❤️ {bpm} BPM</p><p>🌡️ {temp} °C</p></td>
                        <td style='text-align:right;'><p style='font-size:11px; color:#a2d2ff; margin:0;'>REGISTRO</p><p style='color:#ff4d4d; margin:5px 0;'><b>Scan: {alerta['timestamp']}</b></p><p style='color:#ff4d4d; margin:0;'><b>Status: ATIVO</b></p></td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

# Lista Geral de Monitoramento abaixo
st.subheader("⌚ Monitoramento de Dispositivos Wearable")
st.dataframe(df_tel, use_container_width=True)

# Botão para atualizar o painel manualmente
if st.button("🔄 Atualizar Painel"):
    st.rerun()

from sqlalchemy.ext.asyncio import create_async_engine

# Conexao assincrona nativa para a API
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = 'sqlite+aiosqlite:///inspectai.db'
async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

if 'Base' not in locals() and 'Base' not in globals():
    Base = declarative_base()

async def get_db_async():
    async with AsyncSessionLocal() as session:
        yield session
if 'get_db' not in locals() and 'get_db' not in globals():
    get_db = get_db_async
