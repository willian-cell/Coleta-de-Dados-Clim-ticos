# sistema personalizado

from fastapi import FastAPI, Query
import asyncio
import aiohttp
import pandas as pd
from sqlalchemy import create_engine

app = FastAPI()

# Função para obter dados da API do OpenWeatherMap
async def obter_dados_climaticos(session, cidade, chave_api):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={chave_api}&lang=pt_br&units=metric"
    async with session.get(url) as response:
        if response.status == 200:
            dados = await response.json()
            return {
                "cidade": dados["name"],
                "temperatura_atual": dados["main"]["temp"],
                "data_coleta": pd.Timestamp.utcnow(),
                "sensacao_termica": dados["main"]["feels_like"],
                "umidade": dados["main"]["humidity"],
                "descricao_clima": dados["weather"][0]["description"]
            }
    return None

# Rota para buscar os dados de várias cidades
@app.get("/buscar_dados/")
async def buscar_dados(cidades: str, chave_api: str, destino: str = "csv", banco_url: str = ""):
    cidades_lista = cidades.split(",")

    async with aiohttp.ClientSession() as session:
        tarefas = [obter_dados_climaticos(session, cidade.strip(), chave_api) for cidade in cidades_lista]
        resultados = await asyncio.gather(*tarefas)

    dados_coletados = [dado for dado in resultados if dado]

    if not dados_coletados:
        return {"erro": "Nenhum dado foi coletado."}

    df = pd.DataFrame(dados_coletados)

    if destino == "csv":
        # Modo 'a' (append) adiciona novos dados sem apagar os anteriores
        df.to_csv("dados_climaticos.csv", mode='a', index=False, header=not pd.io.common.file_exists("dados_climaticos.csv"))
        
        return {
            "mensagem": "Dados adicionados ao arquivo CSV!",
            "dados": dados_coletados
        }
    
    elif destino == "banco" and banco_url:
        engine = create_engine(banco_url)

        # Adiciona novos dados sem apagar os registros antigos
        df.to_sql("dados_clima", con=engine, if_exists="append", index=False)
        
        return {
            "mensagem": "Dados adicionados ao banco de dados!",
            "dados": dados_coletados
        }

    return {"erro": "Destino inválido"}
