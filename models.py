from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    referral_code = Column(String, unique=True, index=True)
    referred_by = Column(String, nullable=True)  # чей код использовал
    balance = Column(Integer, default=0)  # например, бонусы за рефералов

    numbers = relationship("Number", back_populates="owner")

class Number(Base):
    __tablename__ = "numbers"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True)
    status = Column(String)  # например: "active", "used", "cancelled"
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="numbers")
