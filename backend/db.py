import os
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()
SessionLocal = None
engine = None


def init_engine():
    global engine, SessionLocal
    if not DATABASE_URL:
        return None

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine


def init_db():
    if init_engine() is None:
        return False

    Base.metadata.create_all(bind=engine)
    return True


def get_session():
    if SessionLocal is None:
        return None
    return SessionLocal()


def db_available():
    return DATABASE_URL is not None and SessionLocal is not None


class ProductRequest(Base):
    __tablename__ = "product_requests"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    strength = Column(Float, nullable=False)
    weight_capacity = Column(Float, nullable=False)
    biodegradability_score = Column(Float, nullable=False)
    recyclability_percentage = Column(Float, nullable=False)
    fragility_level = Column(Float, nullable=False)
    shipping_type = Column(String(50), nullable=False)

    raw_payload = Column(Text, nullable=True)

    recommendations = relationship("Recommendation", back_populates="request")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("product_requests.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    material_type = Column(String(50), nullable=False)
    predicted_cost = Column(Float, nullable=False)
    predicted_co2 = Column(Float, nullable=False)
    rank_score = Column(Float, nullable=False)
    environmental_score = Column(Float, nullable=False)

    request = relationship("ProductRequest", back_populates="recommendations")
