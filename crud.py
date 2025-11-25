import csv
import os
from datetime import datetime
from init_db import Customer, Order
from sqlalchemy.orm import Session

CSV_FILE = 'clients_100.csv'


def read_customers_from_csv():
    customers = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer = Customer(
                    id=int(row['ID']),
                    full_name=row['ФИО'],
                    contact_info=row['Контактная информация'],
                    registration_date=datetime.strptime(row['Дата регистрации'], '%Y-%m-%d'),
                    notes=row['Примечания'] if row['Примечания'] else None
                )
                customers.append(customer)
    return customers


def write_customers_to_csv(customers):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['ID', 'ФИО', 'Контактная информация', 'Email', 'Телефон', 'Дата регистрации', 'Примечания']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in customers:
            writer.writerow({
                'ID': c.id,
                'ФИО': c.full_name,
                'Контактная информация': c.contact_info,
                'Email': '',  
                'Телефон': '',
                'Дата регистрации': c.registration_date.strftime('%Y-%m-%d'),
                'Примечания': c.notes or ''
            })


def create_customer(db: Session, full_name: str, contact_info: str, notes: str = None):
    customers = read_customers_from_csv()
    next_id = max((c.id for c in customers), default=0) + 1
    registration_date = datetime.utcnow()
    customer = Customer(
        id=next_id,
        full_name=full_name,
        contact_info=contact_info,
        registration_date=registration_date,
        notes=notes
    )
    customers.append(customer)
    write_customers_to_csv(customers)
    return customer


def get_customers(db: Session):
    return read_customers_from_csv()


def get_customer_by_id(db: Session, customer_id: int):
    customers = read_customers_from_csv()
    for c in customers:
        if c.id == customer_id:
            return c
    return None


def update_customer(db: Session, customer_id: int, full_name: str = None, contact_info: str = None, notes: str = None):
    customers = read_customers_from_csv()
    for c in customers:
        if c.id == customer_id:
            if full_name:
                c.full_name = full_name
            if contact_info:
                c.contact_info = contact_info
            if notes is not None:
                c.notes = notes
            write_customers_to_csv(customers)
            return c
    return None


def delete_customer(db: Session, customer_id: int):
    customers = read_customers_from_csv()
    new_customers = [c for c in customers if c.id != customer_id]
    if len(new_customers) < len(customers):
        write_customers_to_csv(new_customers)
        return True
    return False


def create_order(db: Session, customer_id: int, description: str, amount: float):
    order = Order(
        customer_id=customer_id,
        description=description,
        amount=amount
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_orders(db: Session):
    orders = db.query(Order).all()
    for o in orders:
        o.customer = get_customer_by_id(None, o.customer_id)
    return orders


def get_order_by_id(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.customer = get_customer_by_id(None, order.customer_id)
    return order


def update_order(db: Session, order_id: int, description: str = None, amount: float = None):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        if description:
            order.description = description
        if amount is not None:
            order.amount = amount
        db.commit()
        db.refresh(order)
    return order


def delete_order(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        db.delete(order)
        db.commit()
        return True
    return False
