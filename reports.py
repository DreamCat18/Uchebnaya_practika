import csv
from crud import get_customers, get_orders


def generate_customer_report(db):
    """Генерирует отчет по клиентам в CSV."""
    customers = get_customers(db)
    with open('customer_report.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID',
            'ФИО',
            'Контакты',
            'Дата регистрации',
            'Примечания'
        ])
        for c in customers:
            writer.writerow([
                c.id,
                c.full_name,
                c.contact_info,
                c.registration_date.strftime('%Y-%m-%d'),
                c.notes or ''
            ])


def generate_orders_report(db):
    """Генерирует отчет по заказам в CSV."""
    orders = get_orders(db)
    with open('orders_report.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Клиент', 'Описание', 'Сумма', 'Дата'])
        for o in orders:
            writer.writerow([
                o.id,
                o.customer.full_name,
                o.description,
                o.amount,
                o.order_date.strftime('%Y-%m-%d')
            ])


def generate_customers_by_date_report(db, start_date, end_date):
    """Генерирует отчет по клиентам за период в CSV."""
    customers = get_customers(db)
    filtered = [
        c for c in customers if start_date <= c.registration_date <= end_date
    ]
    with open(
        'customers_by_date_report.csv', 
        'w', 
        newline='', 
        encoding='utf-8'
    ) as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID',
            'ФИО',
            'Контакты',
            'Дата регистрации',
            'Примечания'
        ])
        for c in filtered:
            writer.writerow([
                c.id,
                c.full_name,
                c.contact_info,
                c.registration_date.strftime('%Y-%m-%d'),
                c.notes or ''
            ])
