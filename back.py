from fastapi import FastAPI
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime

app = FastAPI()

# Lista para armazenar consultas
consulta_de_dados = []

# Função para obter dados da API do OpenWeatherMap
async def obter_dados_climaticos(session, cidade, chave_api):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={chave_api}&lang=pt_br&units=metric"
    async with session.get(url) as response:
        if response.status == 200:
            dados = await response.json()

            # Obtém a data/hora UTC e formata para o formato brasileiro
            data_coleta = datetime.utcnow().strftime("%d/%m/%Y %H:%M")

            return {
                "Cidade": dados["name"],
                "Temperatura Atual": dados["main"]["temp"],
                "Data da Coleta": data_coleta,
                "Sensação Térmica": dados["main"]["feels_like"],
                "Umidade": dados["main"]["humidity"],
                "Descrição do Clima": dados["weather"][0]["description"]
            }
    return None

# Rota para buscar os dados de várias cidades
@app.get("/buscar_dados/")
async def buscar_dados(cidades: str, chave_api: str):
    cidades_lista = [cidade.strip() for cidade in cidades.split(",")]

    async with aiohttp.ClientSession() as session:
        tarefas = [obter_dados_climaticos(session, cidade, chave_api) for cidade in cidades_lista]
        resultados = await asyncio.gather(*tarefas)

    dados_coletados = [dado for dado in resultados if dado]

    if not dados_coletados:
        return {"erro": "Nenhum dado foi coletado."}

    consulta_de_dados.extend(dados_coletados)
    df = pd.DataFrame(consulta_de_dados)
    
    return {
        "mensagem": "Dados coletados com sucesso!",
        "dados": dados_coletados
    }

# Rota para baixar todas as consultas
@app.get("/baixar_dados/")
def baixar_dados(formato: str = "csv"):
    df = pd.DataFrame(consulta_de_dados)
    
    if df.empty:
        return {"erro": "Nenhum dado disponível para download."}
    
    if formato == "csv":
        df.to_csv("dados_climaticos.csv", index=False)
        return {"mensagem": "Arquivo CSV gerado com sucesso!"}
    elif formato == "excel":
        df.to_excel("dados_climaticos.xlsx", index=False)
        return {"mensagem": "Arquivo Excel gerado com sucesso!"}
    
    return {"erro": "Formato inválido!"}


    # pip install fastapi uvicorn aiohttp pandas openpyxl

