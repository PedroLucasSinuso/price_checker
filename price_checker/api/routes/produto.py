from fastapi import APIRouter, Depends, HTTPException
from price_checker.api.deps import get_produto_repository
from price_checker.application.services.produto_service import ProdutoService
from price_checker.schemas.produto_schema import ProdutoResponse
from price_checker.domain.value_objects.codigo import Codigo
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=list[ProdutoResponse])
def listar_produtos(limit: int = 50, offset: int = 0, repo=Depends(get_produto_repository)):
    logger.info("Listando produtos | limit=%s offset=%s", limit, offset)

    service = ProdutoService(repo)
    return [ProdutoResponse.model_validate(p) for p in service.listar_paginado(limit=limit, offset=offset)]


@router.get("/{codigo}", response_model=ProdutoResponse)
def obter_produto(codigo: str, repo=Depends(get_produto_repository)):
    logger.info("Busca de produto | codigo=%s", codigo)

    service = ProdutoService(repo)

    try:
        codigo_valido = Codigo(codigo)
    except ValueError:
        raise HTTPException(status_code=400, detail="Código inválido")

    produto = service.obter_por_codigo(codigo_valido.valor)

    if not produto:
        logger.error("Produto não encontrado na API | codigo=%s", codigo)
        
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    response = ProdutoResponse.model_validate(produto)
    response.codigo_buscado = codigo_valido.valor

    return response