from pathlib import Path
from price_checker.application.loaders.query_loader import BaseQueryLoader


class BiQueryLoader(BaseQueryLoader):
    BASE_DIR = Path(__file__).resolve().parent / "queries"
