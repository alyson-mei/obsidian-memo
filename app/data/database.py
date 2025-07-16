from sqlalchemy.orm import declarative_base

engine = None
AsyncSessionLocal = None
Base = declarative_base()