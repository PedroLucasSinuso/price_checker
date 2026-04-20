from fastapi import FastAPI
from price_checker.api.routes import produto, cache_status
from price_checker.core.logging_config import setup_logging

setup_logging()

app = FastAPI(title="Price Checker API")

app.include_router(produto.router)
app.include_router(cache_status.router)