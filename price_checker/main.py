from fastapi import FastAPI
from price_checker.api.routes import produto, cache_status
from price_checker.api.routes import auth
from price_checker.api.routes import admin
from price_checker.core.logging_config import setup_logging
from price_checker.core.config import settings

setup_logging()

app = FastAPI(title="Price Checker API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produto.router)
app.include_router(cache_status.router)
app.include_router(auth.router)
app.include_router(admin.router)