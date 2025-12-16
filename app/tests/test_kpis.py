# backend/app/tests/test_kpis.py

from sqlmodel import create_engine, SQLModel, Session
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import pytest
import os
from unittest.mock import patch

# Importar o aplicativo principal e os modelos
# Certifique-se de que a sua estrutura de importação funciona (pode precisar de um __init__.py vazio)
from app.main import app, get_session
from app.models import FuelData

# --- Configuração de Banco de Dados de Teste ---

# Criar um engine SQLite em memória para testes
TEST_DATABASE_URL = "sqlite:///./test.db"
# Usar `connect_args={"check_same_thread": False}` para SQLite com FastAPI
engine = create_engine(TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}) 

def create_db_and_tables():
    """Cria tabelas no banco de dados de teste (SQLite)."""
    SQLModel.metadata.create_all(engine)

def get_session_override():
    """Substitui o gerador de sessão do FastAPI para usar o DB de teste."""
    with Session(engine) as session:
        yield session

# Aplica a substituição (override) do gerador de dependência
app.dependency_overrides[get_session] = get_session_override
client = TestClient(app)

# --- Fixture de Teste ---

@pytest.fixture(name="session")
def session_fixture():
    """Configura o DB antes de cada teste e limpa depois."""
    create_db_and_tables() # Cria as tabelas
    with Session(engine) as session:
        yield session
    # Após o teste, dropa as tabelas para isolamento
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client_with_data")
def client_with_data_fixture(session: Session):
    """Popula o DB de teste com dados para agregação."""
    
    # Preços fixos para cálculo fácil:
    # Gasolina: (6.0 + 7.0) / 2 = 6.5
    # Etanol: (4.0 + 4.0 + 4.0) / 3 = 4.0
    
    data_points = [
        # Gasolina (Total: 13.0, Count: 2)
        FuelData(posto_id="P1", nome_posto="A", cidade="R", estado="PE", preco_venda=6.0, volume_vendido=50.0, tipo_combustivel="Gasolina", nome_motorista="M1", cpf_motorista="1", placa_veiculo="X1", tipo_veiculo="Carro", data_coleta=datetime.utcnow() - timedelta(days=1)),
        FuelData(posto_id="P2", nome_posto="B", cidade="R", estado="PE", preco_venda=7.0, volume_vendido=30.0, tipo_combustivel="Gasolina", nome_motorista="M2", cpf_motorista="2", placa_veiculo="X2", tipo_veiculo="Moto", data_coleta=datetime.utcnow()),
        
        # Etanol (Total: 12.0, Count: 3)
        FuelData(posto_id="P3", nome_posto="C", cidade="R", estado="PE", preco_venda=4.0, volume_vendido=100.0, tipo_combustivel="Etanol", nome_motorista="M3", cpf_motorista="3", placa_veiculo="X3", tipo_veiculo="Caminhão Leve", data_coleta=datetime.utcnow() - timedelta(days=2)),
        FuelData(posto_id="P4", nome_posto="D", cidade="R", estado="SP", preco_venda=4.0, volume_vendido=200.0, tipo_combustivel="Etanol", nome_motorista="M4", cpf_motorista="4", placa_veiculo="X4", tipo_veiculo="Carreta", data_coleta=datetime.utcnow()),
        FuelData(posto_id="P5", nome_posto="E", cidade="R", estado="SP", preco_venda=4.0, volume_vendido=500.0, tipo_combustivel="Etanol", nome_motorista="M5", cpf_motorista="5", placa_veiculo="X5", tipo_veiculo="Carreta", data_coleta=datetime.utcnow()),
    ]

    for data in data_points:
        session.add(data)
    session.commit()
    
    return client

# --- Teste de KPI ---

def test_calculate_average_price_correctly(client_with_data: TestClient):
    """
    Verifica se o cálculo da média de preço por tipo de combustível 
    está correto (Requisito: Testes para garantir que o cálculo está correto).
    """
    response = client_with_data.get("/api/v1/kpis/media-preco")
    assert response.status_code == 200
    
    results = response.json()
    
    # Converte a lista de dicionários em um dicionário para busca fácil
    price_map = {item['tipo_combustivel']: item['media_preco'] for item in results}
    
    # Verificação 1: Gasolina (Média esperada: 6.5)
    gasolina_media = price_map.get("Gasolina")
    assert gasolina_media is not None
    assert round(gasolina_media, 2) == 6.50
    
    # Verificação 2: Etanol (Média esperada: 4.0)
    etanol_media = price_map.get("Etanol")
    assert etanol_media is not None
    assert round(etanol_media, 2) == 4.00
    
    assert len(results) == 2 # Deve haver apenas 2 tipos de combustível