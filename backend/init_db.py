"""Initialize database with SQLite for development."""
import os
from src.database.connection import Base, engine
from src.database.models import *  # Import all models

# Update database URL to use SQLite
os.environ['DATABASE_URL'] = 'sqlite:///./financial_analyzer.db'

# Recreate engine with SQLite
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./financial_analyzer.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")
    print("Database file: financial_analyzer.db")

