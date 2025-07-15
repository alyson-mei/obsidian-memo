from sqlalchemy import Column, Integer, DateTime, Text
from sqlalchemy.sql import func

from app.data.database import Base

class Time(Base):
    __tablename__ = "time"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    message_light = Column(Text, nullable=False)
    message_dark = Column(Text, nullable=False)
    date = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), onupdate=func.now())