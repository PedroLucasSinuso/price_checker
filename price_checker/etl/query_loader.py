from pathlib import Path

class QueryLoader():
    BASE_DIR = Path(__file__).resolve().parent / "queries"

    @classmethod
    def load(cls, name: str) -> str:
        path = cls.BASE_DIR / f"{name}.sql"
        if not path.is_file():
            raise FileNotFoundError(f"Query {name} não encontrada em {path}")
        return path.read_text(encoding="utf-8")