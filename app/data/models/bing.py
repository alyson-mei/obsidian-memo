from sqlalchemy import Column, Integer, DateTime, Text
from sqlalchemy.sql import func

from app.data.database import Base

class Bing(Base):
    __tablename__ = "bing"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    image_url = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    date = Column(Text, nullable=True)
    copyright = Column(Text, nullable=True)
    page_url = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), onupdate=func.now())
