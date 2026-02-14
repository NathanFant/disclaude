"""Database setup and models."""
from sqlalchemy import create_engine, Column, BigInteger, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class UserProfile(Base):
    """User profile model for Discord to Minecraft linking."""
    __tablename__ = 'user_profiles'

    discord_id = Column(BigInteger, primary_key=True)
    minecraft_username = Column(String, nullable=False)
    minecraft_uuid = Column(String, nullable=False)


# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///disclaude.db')

# Fix Railway's postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"[DATABASE] Connecting to: {DATABASE_URL.split('@')[0]}...")  # Hide credentials

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    print("[DATABASE] Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("[DATABASE] Database initialized")


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let caller close
