"""
Database initialization script
Run this to create all tables in the database
"""
from database import engine, Base
import models  # Import models to register them with Base

def init_database():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()