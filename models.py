from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    contact_info = Column(String, nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String)

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
