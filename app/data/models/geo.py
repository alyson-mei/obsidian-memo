from sqlalchemy import Column, Integer, DateTime, Text
from sqlalchemy.sql import func

from app.data.database import Base

class Geo(Base):
    __tablename__ = "geo"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    place = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    urls = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), onupdate=func.now())