import pytz  # Importando pytz para converter fusos horários

app = FastAPI()

# Lista para armazenar consultas
consulta_de_dados = []

# Definir fuso horário de Brasília
fuso_brasilia = pytz.timezone("America/Sao_Paulo")

# Função para obter dados da API do OpenWeatherMap
async def obter_dados_climaticos(session, cidade, chave_api):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={chave_api}&lang=pt_br&units=metric"
    async with session.get(url) as response:
        if response.status == 200:
            dados = await response.json()

            # Obtendo a hora atual em UTC e convertendo para o horário de Brasília
            data_coleta_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
            data_coleta_brasilia = data_coleta_utc.astimezone(fuso_brasilia)
            data_formatada = data_coleta_brasilia.strftime("%d/%m/%Y %H:%M")

            return {
                "Cidade": dados["name"],
                "Temperatura Atual": dados["main"]["temp"],
                "Data da Coleta": data_formatada,  # Horário de Brasília
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