import streamlit as st
import requests

# URL base do seu backend Flask
API_URL = "http://localhost:5000/api/incidentes"

st.title("🚨 Incidentes em Tempo Real")
st.write("Ocorrências pendentes de tratamento imediato pela equipe de segurança:")

try:
    # 1. Busca os dados filtrados e leves da API
    resposta = requests.get(f"{API_URL}/ativos")
    
    if resposta.status_code == 200:
        incidentes = resposta.json()
        
        if not incidentes:
            st.success("✅ Nenhum incidente ativo detectado no momento. Tudo limpo!")
            
        for inc in incidentes:
            id_incidente = inc['id']
            operador = inc['operador_id']
            
            # Cria colunas no Streamlit para alinhar o texto e o botão perfeitamente na mesma linha
            col_texto, col_botao = st.columns([0.8, 0.2])
            
            with col_texto:
                # Exibe o alerta formatado como na sua imagem original
                st.error(f"⚠️ **Incidente #{id_incidente}** — Desvio de EPI detectado para: **{operador}**")
                
            with col_botao:
                # O key individual impede que o clique em um botão afete os outros alertas
                if st.button("✓ Resolver", key=f"btn_{id_incidente}", use_container_width=True):
                    
                    # 2. Envia o comando de resolução para a rota Flask correspondente
                    res_resolver = requests.post(f"{API_URL}/resolver/{id_incidente}")
                    
                    if res_resolver.status_code == 200:
                        st.toast(f"Incidente #{id_incidente} resolvido!", icon="🔥")
                        # Força o Streamlit a recarregar a tela instantaneamente sem o alerta resolvido
                        st.rerun()
                    else:
                        st.sidebar.error("Erro ao tentar resolver o incidente no servidor.")
                        
            st.markdown("---") # Linha sutil separadora entre alertas
            
    else:
        st.error("❌ Erro ao obter comunicacao com o servidor backend.")

except requests.exceptions.ConnectionError:
    st.warning("🔌 O servidor backend (api_service.py) nao esta respondendo. Certifique-se de que ele esta rodando na porta 5000.")