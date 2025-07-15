from sqlalchemy import Column, Integer, DateTime, Text
from sqlalchemy.sql import func

from app.data.database import Base

class Commit(Base):
    __tablename__ = "commit"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), onupdate=func.now())