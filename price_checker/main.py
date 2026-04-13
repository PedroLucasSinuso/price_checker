from fastapi import FastAPI
from price_checker.api.routes import produto, cache_status

app = FastAPI(title="Price Checker API")

app.include_router(produto.router)
app.include_router(cache_status.router)