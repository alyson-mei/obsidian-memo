from sqlalchemy import Column, Integer, DateTime, Text
from sqlalchemy.sql import func

from app.data.database import Base

class Journal(Base):
    __tablename__ = "journal"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    event = Column(Text, nullable=False)
    journal = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), onupdate=func.now())
