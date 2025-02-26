import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(page_title="Coleta de Dados Climáticos 🌍", layout="wide")

st.title("Coleta de Dados Climáticos 🌍")
st.subheader("Por: Willian Batista Oliveira")
st.subheader("📊 Analista de Dados")

# Entrada de dados
chave_api = st.text_input("🔑 Digite sua chave da API OpenWeatherMap:", type="password")
cidades = st.text_area("📍 Digite as cidades (separadas por vírgula):")
destino = st.radio("📌 Onde deseja salvar os dados?", ["CSV", "Banco de Dados"])

banco_url = ""
if destino == "Banco de Dados":
    banco_url = st.text_input("🔗 Digite a URL do Banco de Dados (SQLAlchemy):")

if st.button("🚀 Coletar Dados"):
    if not chave_api or not cidades:
        st.error("⚠️ Por favor, insira a chave da API e as cidades.")
    else:
        params = {
            "cidades": cidades,
            "chave_api": chave_api,
            "destino": "banco" if destino == "Banco de Dados" else "csv",
            "banco_url": banco_url
        }

        with st.spinner("🔄 Coletando dados... Aguarde!"):
            response = requests.get("http://127.0.0.1:8000/buscar_dados/", params=params)
        
        if response.status_code == 200:
            dados_resposta = response.json()
            st.success(dados_resposta["mensagem"])

            if "dados" in dados_resposta:
                df = pd.DataFrame(dados_resposta["dados"])

                # Exibir dados na interface
                st.subheader("📊 Dados Recentes Coletados")
                st.dataframe(df.style.set_properties(**{
                    'background-color': 'white',
                    'color': 'black',
                    'border-color': 'black'
                }))

                # Botão de download do CSV
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Baixar CSV Atualizado",
                    data=csv,
                    file_name="dados_climaticos.csv",
                    mime="text/csv"
                )

                # Exibir CSV completo acumulado
                if os.path.exists("dados_climaticos.csv"):
                    st.subheader("📂 Histórico Completo")
                    df_historico = pd.read_csv("dados_climaticos.csv")
                    st.dataframe(df_historico)

        else:
            st.error("❌ Erro ao obter os dados. Verifique sua conexão e tente novamente.")
