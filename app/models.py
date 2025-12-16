from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class FuelData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Informações do Posto
    posto_id: str = Field(index=True) # 1. Identificador do Posto [cite: 19]
    nome_posto: str # 2. Nome do Posto [cite: 20]
    cidade: str # 3. Cidade [cite: 21]
    estado: str # 3. Estado [cite: 21]

    # Informações da Coleta
    data_coleta: datetime = Field(default_factory=datetime.utcnow, index=True) # 4. Data da Coleta [cite: 22]
    tipo_combustivel: str = Field(index=True) # 5. Tipo de Combustível (Gasolina, Etanol, Diesel S10) [cite: 23]
    
    # Valores
    preco_venda: float # 6. Preço de Venda (Reais por litro) [cite: 24]
    volume_vendido: float # 7. Volume Vendido (litros) [cite: 25]

    # Informações do Motorista/Veículo
    nome_motorista: str # 8. Nome do Motorista [cite: 26]
    cpf_motorista: str = Field(index=True) # 9. CPF do Motorista 
    placa_veiculo: str # 10. Placa do Veículo [cite: 28]
    tipo_veiculo: str = Field(index=True) # 11. Tipo de Veículo (Carro, Caminhão, etc.) [cite: 29]

# Schema de Ingestão (Herda as regras de FuelData, mas sem ID e data_coleta opcional)
class FuelDataCreate(SQLModel):
    posto_id: str
    nome_posto: str
    cidade: str
    estado: str
    data_coleta: Optional[datetime] = None
    tipo_combustivel: str
    preco_venda: float
    volume_vendido: float
    nome_motorista: str
    cpf_motorista: str
    placa_veiculo: str
    tipo_veiculo: str