from price_checker.db.bootstrap import init_db
from price_checker.etl.dump import dump_postgres_to_sqlite

def run_etl():
    init_db()
    dump_postgres_to_sqlite()

if __name__ == "__main__":
    run_etl()