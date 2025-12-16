# backend/app/main.py (Atualizado com Redis Cache)

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from .models import FuelData, FuelDataCreate
from .database import create_db_and_tables, get_session
import logging
import os
from redis import asyncio as aioredis # Importação assíncrona para FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache # Decorador para aplicar o cache

logger = logging.getLogger(__name__)

app = FastAPI(
    title="V-Lab Fuel Monitoring API",
    description="API para monitoramento de mercado de combustíveis.",
)

@app.on_event("startup")
async def on_startup():
    """Garante que as tabelas sejam criadas e inicializa o cache Redis."""
    create_db_and_tables()
    
    # Inicializa Redis Cache
    # Obtém a URL do ambiente (do docker-compose.yml)
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0") 
    redis = aioredis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info("Cache Redis inicializado.")

# ... (Rota de Ingestão: @app.post("/api/v1/coletas/ingest") - SEM CACHE) ...

# Rota de Média de Preço por Combustível (AGORA COM CACHE)
from sqlmodel.sql.expression import func

@app.get("/api/v1/kpis/media-preco")
@cache(expire=300) # Cache de 5 minutos (300 segundos)
def get_average_price(session: Session = Depends(get_session)):
    """Calcula a média de preço por tipo de combustível (Cacheada por 5 min)."""
    
    # Esta lógica só será executada se o cache expirar ou for a primeira chamada
    logger.info("Executando cálculo de média de preço no DB (Sem Cache)")
    
    statement = select(
        FuelData.tipo_combustivel,
        func.avg(FuelData.preco_venda).label("media_preco")
    ).group_by(FuelData.tipo_combustivel)
    
    results = session.exec(statement).all()
    
    return [{"tipo_combustivel": res[0], "media_preco": round(res[1], 3)} for res in results]

# Rota de Volume Consumido por Tipo de Veículo (AGORA COM CACHE)
@app.get("/api/v1/kpis/consumo-por-veiculo")
@cache(expire=300) # Cache de 5 minutos (300 segundos)
def get_volume_by_vehicle(session: Session = Depends(get_session)):
    """Calcula o volume total consumido agrupado por tipo de veículo (Cacheada por 5 min)."""
    
    logger.info("Executando cálculo de volume por veículo no DB (Sem Cache)")
    
    statement = select(
        FuelData.tipo_veiculo,
        func.sum(FuelData.volume_vendido).label("volume_total")
    ).group_by(FuelData.tipo_veiculo).order_by(func.sum(FuelData.volume_vendido).desc())
    
    results = session.exec(statement).all()
    
    return [{"tipo_veiculo": res[0], "volume_total": round(res[1], 2)} for res in results]

# ... (Outras Rotas de Consulta - Listagem Geral e Relatório de Motorista - Sem Cache por conta dos filtros)
# Rota de Volume Consumido por Tipo de Veículo [cite: 45]
from sqlmodel.sql.expression import func

@app.get("/api/v1/kpis/consumo-por-veiculo")
def get_volume_by_vehicle(session: Session = Depends(get_session)):
    """Calcula o volume total consumido agrupado por tipo de veículo."""
    
    # Consulta SQLModel com agregação (SUM e GROUP BY)
    statement = select(
        FuelData.tipo_veiculo,
        func.sum(FuelData.volume_vendido).label("volume_total")
    ).group_by(FuelData.tipo_veiculo).order_by(func.sum(FuelData.volume_vendido).desc())
    
    results = session.exec(statement).all()
    
    return [{"tipo_veiculo": res[0], "volume_total": round(res[1], 2)} for res in results]

# Rota de Listagem Geral com Paginação (Simplificada) [cite: 40]
@app.get("/api/v1/coletas")
def get_coletas(
    session: Session = Depends(get_session),
    page: int = 1,
    size: int = 10,
    tipo_combustivel: Optional[str] = None,
    cidade: Optional[str] = None
):
    """Listagem geral de coletas com filtros e paginação."""
    offset = (page - 1) * size
    
    # Cria a base da query
    query = select(FuelData)
    
    # Aplica filtros (WHERE clause)
    if tipo_combustivel:
        query = query.where(FuelData.tipo_combustivel == tipo_combustivel)
    if cidade:
        query = query.where(FuelData.cidade == cidade)
        
    # Aplica paginação (OFFSET e LIMIT)
    query = query.offset(offset).limit(size).order_by(FuelData.data_coleta.desc())

    coletas = session.exec(query).all()
    
    # Para a paginação completa, você precisaria de um COUNT separado.
    return coletas

    #
# Rota de Relatório de Motorista [cite: 46]
@app.get("/api/v1/relatorio/motorista")
def get_driver_report(
    session: Session = Depends(get_session),
    cpf: Optional[str] = None,
    nome: Optional[str] = None
):
    """Busca histórico de abastecimento, filtrando por CPF ou Nome."""
    
    if not cpf and not nome:
        raise HTTPException(status_code=400, detail="Forneça CPF ou Nome para buscar o motorista.")

    query = select(FuelData)
    
    if cpf:
        # Busca exata pelo CPF
        query = query.where(FuelData.cpf_motorista == cpf)
    elif nome:
        # Busca por nome (LIKE)
        query = query.where(FuelData.nome_motorista.ilike(f"%{nome}%"))
        
    results = session.exec(query.order_by(FuelData.data_coleta.desc())).all()

    # Mascaramento/Validação na Exibição 
    # No Frontend, você pode exibir apenas os últimos 4 dígitos do CPF (ex: ***.***.***-78)
    
    return results