from fastapi import APIRouter, Depends, HTTPException
from price_checker.api.deps import get_produto_repository, get_current_user, require_supervisor
from price_checker.application.services.produto_service import ProdutoService
from price_checker.schemas.produto_schema import ProdutoPublicResponse, ProdutoResponse
from price_checker.domain.value_objects.codigo import Codigo
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def _buscar(codigo: str, repo, schema_class):
    try:
        codigo_valido = Codigo(codigo)
    except ValueError:
        raise HTTPException(status_code=400, detail="Código inválido")

    produto = ProdutoService(repo).obter_por_codigo(codigo_valido.valor)

    if not produto:
        logger.warning("Produto não encontrado na API | codigo=%s", codigo)
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    response = schema_class.model_validate(produto)
    response.codigo_buscado = codigo_valido.valor
    return response


@router.get("/", response_model=list[ProdutoPublicResponse])
def listar_produtos(
    limit: int = 50,
    offset: int = 0,
    repo=Depends(get_produto_repository),
    _user=Depends(get_current_user),
):
    logger.info("Listando produtos | limit=%s offset=%s", limit, offset)
    service = ProdutoService(repo)
    return [ProdutoPublicResponse.model_validate(p) for p in service.listar_paginado(limit=limit, offset=offset)]


@router.get("/{codigo}", response_model=ProdutoPublicResponse)
def obter_produto_publico(
    codigo: str,
    repo=Depends(get_produto_repository),
    _user=Depends(get_current_user),
):
    logger.info("Busca pública | codigo=%s", codigo)
    return _buscar(codigo, repo, ProdutoPublicResponse)


@router.get("/{codigo}/completo", response_model=ProdutoResponse)
def obter_produto_completo(
    codigo: str,
    repo=Depends(get_produto_repository),
    _user=Depends(require_supervisor),
):
    logger.info("Busca completa | codigo=%s", codigo)
    return _buscar(codigo, repo, ProdutoResponse)