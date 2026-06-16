from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class ImageConfig(Base):
    __tablename__ = "image_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, nullable=False)
    slot = Column(Integer, nullable=False)
    image_path = Column(Text, nullable=True)
    alpha = Column(String(20), default="0.5")
    beta = Column(String(20), default="0.3")
    rho = Column(String(20), default="0.8")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
