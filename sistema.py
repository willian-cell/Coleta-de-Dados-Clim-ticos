import streamlit as st
import requests
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Coleta de Dados Climáticos 🌍", layout="wide")

st.title("Coleta de Dados Climáticos 🌍")
st.subheader("Por: Willian Batista Oliveira")
st.subheader("📊 Analista de Dados")

# Lista para armazenar consultas
if "consulta_de_dados" not in st.session_state:
    st.session_state.consulta_de_dados = []

# Capturar nome do usuário localmente
usuario = st.text_input("👤 Digite seu nome:", value="Usuário", max_chars=50)

# Entrada de dados
chave_api = "42d01a312f6740b003d77ae949a14376"
cidades = st.text_area("📍 Digite as cidades (separadas por vírgula):")
destino = st.radio("📌 Como deseja baixar seus dados?", ["CSV", "Excel"])  # Removido Word

if st.button("🚀 Coletar Dados"):
    if not chave_api or not cidades:
        st.error("⚠️ Por favor, insira a chave da API e as cidades.")
    else:
        cidades_lista = [cidade.strip() for cidade in cidades.split(",")]
        dados_coletados = []
        
        with st.spinner("🔄 Coletando dados... Aguarde!"):
            for cidade in cidades_lista:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={chave_api}&lang=pt_br&units=metric"
                response = requests.get(url)
                
                if response.status_code == 200:
                    dados = response.json()
                    dados_coletados.append({
                        "Usuário": usuario,
                        "Cidade": dados["name"],
                        "Temperatura Atual": dados["main"]["temp"],
                        "Sensação Térmica": dados["main"]["feels_like"],
                        "Umidade": dados["main"]["humidity"],
                        "Descrição do Clima": dados["weather"][0]["description"],
                        "Data da Coleta": datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                    })
            
        if dados_coletados:
            st.session_state.consulta_de_dados.extend(dados_coletados)
            df = pd.DataFrame(st.session_state.consulta_de_dados)
            st.success("✅ Dados coletados com sucesso!")
            
            # Exibir a última consulta
            st.subheader("📌 Última Consulta")
            st.dataframe(pd.DataFrame([dados_coletados[-1]]))
            
            # Exibir todas as cidades consultadas
            st.subheader("📊 Histórico Completo de Consultas")
            st.dataframe(df)
            
            # Opções de download
            if destino == "CSV":
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Baixar CSV", csv, "dados_climaticos.csv", "text/csv")
            elif destino == "Excel":
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name="Dados Climáticos")
                st.download_button("📥 Baixar Excel", excel_buffer.getvalue(), "dados_climaticos.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.error("❌ Nenhum dado foi coletado. Verifique a chave da API e os nomes das cidades.")
