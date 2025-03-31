from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import threading

# Database setup
DATABASE_URI = 'postgresql://neondb_owner:npg_TEZ0qbhi7pMx@ep-royal-hill-a8ya3jn7-pooler.eastus2.azure.neon.tech/neondb?sslmode=require'

engine = create_engine(
    DATABASE_URI,
    pool_size=10,                # Max number of connections in the pool
    max_overflow=20,             # Extra connections allowed beyond the pool size
    pool_timeout=3600,           # Wait up to 1 hour (3600 seconds) for a connection
    pool_recycle=3600            # Recycle connections every 1 hour
)

Base = declarative_base()

# Scoped session to prevent concurrency issues
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db_session = scoped_session(SessionFactory)

# Ensure session cleanup (important for preventing PendingRollbackError)
def get_session():
    """Get a new session with proper exception handling."""
    session = db_session()
    try:
        yield session
        session.commit()  # Commit if no errors
    except Exception as e:
        session.rollback()  # Rollback on error
        raise e
    finally:
        session.close()  # Close session to avoid connection leaks

# Create tables
def create_tables():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    create_tables()
    print("Database tables created successfully!")
