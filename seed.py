import requests
from faker import Faker
import random
from datetime import datetime, timedelta

# URL do seu serviço Backend (dentro do Docker, o hostname é 'backend')
# Se for rodar localmente fora do docker-compose: 'http://localhost:8000'
# Se for rodar DENTRO de um container separado no docker-compose: 'http://backend:8000'
API_INGEST_URL = "http://localhost:8000/api/v1/coletas/ingest" # Assume que você executará localmente por conveniência

# Dados de simulação
fake = Faker('pt_BR')
COMBUSTIVEIS = ["Gasolina", "Etanol", "Diesel S10"] [cite: 23]
TIPOS_VEICULO = ["Carro", "Moto", "Caminhão Leve", "Carreta", "Ônibus"] [cite: 29]
POSTOS = [
    {"id": "0001", "nome": "Posto Brasil", "cidade": "Recife", "estado": "PE"},
    {"id": "0002", "nome": "Posto Via Rápida", "cidade": "São Paulo", "estado": "SP"},
    {"id": "0003", "nome": "Posto Litoral", "cidade": "Salvador", "estado": "BA"},
]

def generate_realistic_price(fuel_type):
    """Preços realistas randômicos.""" [cite: 35]
    if fuel_type == "Gasolina":
        return round(random.uniform(5.00, 7.50), 2)
    elif fuel_type == "Etanol":
        return round(random.uniform(3.50, 5.50), 2)
    elif fuel_type == "Diesel S10":
        return round(random.uniform(5.80, 7.00), 2)
    return 0.0

def generate_volume(vehicle_type):
    """Volumes vendidos realistas.""" [cite: 25]
    if vehicle_type in ["Carreta", "Ônibus"]:
        return round(random.uniform(150, 500), 2) # Alto volume
    elif vehicle_type == "Carro":
        return round(random.uniform(20, 70), 2)
    elif vehicle_type == "Moto":
        return round(random.uniform(5, 15), 2)
    elif vehicle_type == "Caminhão Leve":
        return round(random.uniform(50, 150), 2)
    return 0.0

def generate_data():
    """Gera um único registro de coleta de dados fictício."""
    posto = random.choice(POSTOS)
    fuel = random.choice(COMBUSTIVEIS)
    vehicle = random.choice(TIPOS_VEICULO)
    
    # Simula datas nos últimos 30 dias para o gráfico de evolução 
    days_ago = random.randint(1, 30)
    data_coleta = datetime.now() - timedelta(days=days_ago)

    data = {
        "posto_id": posto["id"],
        "nome_posto": posto["nome"],
        "cidade": posto["cidade"],
        "estado": posto["estado"],
        "data_coleta": data_coleta.isoformat(),
        "tipo_combustivel": fuel,
        "preco_venda": generate_realistic_price(fuel),
        "volume_vendido": generate_volume(vehicle),
        "nome_motorista": fake.name(),
        "cpf_motorista": fake.cpf().replace('.', '').replace('-', ''), # CPF sem formatação
        "placa_veiculo": fake.license_plate(),
        "tipo_veiculo": vehicle,
    }
    return data

def run_ingestion(count: int = 200):
    """Faz chamadas HTTP POST para o Backend.""" [cite: 36]
    print(f"Iniciando a ingestão de {count} registros...")
    
    for i in range(count):
        data = generate_data()
        try:
            response = requests.post(API_INGEST_URL, json=data)
            if response.status_code != 201:
                print(f"Erro na ingestão do registro {i+1}: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"ERRO: Não foi possível conectar ao Backend em {API_INGEST_URL}. Verifique se o serviço 'backend' está rodando.")
            break
        
        if (i + 1) % 50 == 0:
            print(f"  > {i+1} registros enviados.")

    print("Ingestão concluída.")

if __name__ == "__main__":
    # Necessário instalar requests e faker (já inclusos no requirements.txt)
    # python seed.py 
    import argparse
    parser = argparse.ArgumentParser(description="Script de ingestão de dados fictícios.")
    parser.add_argument('-c', '--count', type=int, default=200, help='Número de registros a serem gerados e enviados.')
    args = parser.parse_args()
    run_ingestion(args.count)