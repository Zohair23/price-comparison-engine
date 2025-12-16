# create_tables_postgres.py
# Run this script once after updating your DATABASE_URL to PostgreSQL
from database import Base, engine

if __name__ == "__main__":
    print("Creating all tables in the PostgreSQL database...")
    Base.metadata.create_all(bind=engine)
    print("Done.")
