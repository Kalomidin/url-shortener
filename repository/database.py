from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres:password@" "localhost:5433/memento-ai-db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Ensure the function utc_timestamp() is marked as immutable
with engine.connect() as conn:
    conn.execute(
        text("""
        CREATE OR REPLACE FUNCTION public.utc_timestamp() RETURNS timestamp with time zone
        LANGUAGE sql IMMUTABLE
        AS $$
            SELECT statement_timestamp() AT TIME ZONE 'UTC';
        $$;
    """)
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
