from price_checker.db.bootstrap import init_db
from price_checker.etl.dump import dump_postgres_to_sqlite



def main():
    dump_postgres_to_sqlite()

if __name__ == "__main__":
    init_db()
    main()
