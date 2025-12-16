from sqlmodel import create_engine, SQLModel, Session
import os

# A URL é lida do docker-compose.yml via environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False) # echo=True para ver o SQL gerado

def create_db_and_tables():
    """Cria o banco e as tabelas (se não existirem)"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Retorna um gerador para injeção de dependência do FastAPI"""
    with Session(engine) as session:
        yield session