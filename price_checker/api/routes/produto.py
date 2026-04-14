from fastapi import APIRouter, Depends, HTTPException
from price_checker.api.deps import get_produto_repository
from price_checker.services.produto_service import ProdutoService
from price_checker.schemas.produto_schema import ProdutoResponse

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=list[ProdutoResponse])
def listar_produtos(limit: int = 50, offset: int = 0, repo=Depends(get_produto_repository)):
    service = ProdutoService(repo)
    return [ProdutoResponse.model_validate(p) for p in service.listar_paginado(limit=limit, offset=offset)]


@router.get("/{codigo}", response_model=ProdutoResponse)
def obter_produto(codigo: str, repo=Depends(get_produto_repository)):
    service = ProdutoService(repo)

    try:
        produto = service.obter_com_metricas(codigo)
    except ValueError:
        raise HTTPException(status_code=400, detail="Código inválido")

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return produto