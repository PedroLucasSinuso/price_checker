from ..db.database import Base
from sqlalchemy import Column, Integer, String, Float

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_chamada = Column(String, index=True)
    nome = Column(String, index=True)
    grupo = Column(String, index=True)
    familia = Column(String, index=True)
    preco_venda = Column(Float)
    preco_custo = Column(Float)
    estoque = Column(Integer)
    codigo = Column(String, index=True)
