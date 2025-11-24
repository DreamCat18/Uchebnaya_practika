from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime, 
    Text, 
    ForeignKey, 
    Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Customer(Base):
    """Модель Клиента, представляющая клиента компании."""
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    contact_info = Column(String(255), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    """Модель Заказа, представляющая заказ клиента. """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)

    customer = relationship("Customer", back_populates="orders")