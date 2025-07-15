from sqlalchemy import Column, Integer, DateTime, Text
from sqlalchemy.sql import func

from app.data.database import Base
    
class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), onupdate=func.now())
