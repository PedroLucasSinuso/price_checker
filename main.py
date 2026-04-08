from db.boostrap import init_db
from .etl.dump import dump_postgres_to_sqlite



def main():
    dump_postgres_to_sqlite()

if __name__ == "__main__":
    init_db()
    main()