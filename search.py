from sqlalchemy.orm import Session
from models import Customer
from datetime import datetime


def search_customers_by_name(db: Session, name: str):
    """Поиск клиентов по полному имени."""
    return db.query(Customer).filter(
        Customer.full_name.ilike(f'%{name}%')
    ).all()


def search_customers_by_contact(db: Session, contact: str):
    """Поиск клиентов по контактной информации."""
    return db.query(Customer).filter(
        Customer.contact_info.ilike(f'%{contact}%')
    ).all()


def search_customers_by_date_range(
        db: Session,
        start_date: datetime,
        end_date: datetime
):
    """Поиск клиентов, зарегистрированных в указанном диапазоне дат."""
    return db.query(Customer).filter(
        Customer.registration_date >= start_date,
        Customer.registration_date <= end_date
    ).all()


def search_customers_by_notes(db: Session, keyword: str):
    """Поиск клиентов по ключевому слову в примечаниях."""
    return db.query(Customer).filter(
        Customer.notes.ilike(f'%{keyword}%')
    ).all()


def search_customers_comprehensive(db: Session, search_term: str):
    """Комплексный поиск клиентов по всем полям."""
    return db.query(Customer).filter(
        (Customer.full_name.ilike(f'%{search_term}%')) |
        (Customer.contact_info.ilike(f'%{search_term}%')) |
        (Customer.notes.ilike(f'%{search_term}%'))
    ).all()


def search_customers_by_phone(db: Session, phone: str):
    """Поиск клиентов по номеру телефона."""
    return db.query(Customer).filter(
        Customer.contact_info.ilike(f'%{phone}%')
    ).all()


def search_customers_by_email(db: Session, email: str):
    """Поиск клиентов по email адресу."""
    return db.query(Customer).filter(
        Customer.contact_info.ilike(f'%{email}%')
    ).all()