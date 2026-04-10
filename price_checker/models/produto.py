from price_checker.db.database import Base
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

# Model: representa a entidade persistida e mapeada para a tabela no banco.
class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo_chamada: Mapped[str] = mapped_column(String, index=True)
    nome: Mapped[str] = mapped_column(String, index=True)
    grupo: Mapped[str] = mapped_column(String, index=True)
    familia: Mapped[str] = mapped_column(String, index=True)
    preco_venda: Mapped[float] = mapped_column(Float)
    preco_custo: Mapped[float] = mapped_column(Float)
    estoque: Mapped[int] = mapped_column(Integer)
    codigo: Mapped[str] = mapped_column(String, index=True)

    @property
    def markup(self) -> float:
        if self.preco_custo == 0:
            return 0.0
        return (self.preco_venda - self.preco_custo) / self.preco_custo
    
    @property
    def margem(self) -> float:
        if self.preco_venda == 0:
            return 0.0
        return (self.preco_venda - self.preco_custo) / self.preco_venda

