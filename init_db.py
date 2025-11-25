# init_db.py - Инициализация базы данных
from database import engine, Base, SessionLocal
from models import Customer, Order
import csv
from datetime import datetime


def init_database():
    """Создание таблиц в базе данных"""
    print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")


def import_sample_data():
    """Импорт тестовых данных из CSV файлов"""
    db = SessionLocal()

    try:
        # Импорт клиентов
        print("Импорт клиентов...")
        with open('clients_100.csv', 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                customer = Customer(
                    full_name=row['ФИО'],
                    contact_info=row['Контактная информация'],
                    registration_date=datetime.strptime(row['Дата регистрации'], '%Y-%m-%d'),
                    notes=row['Примечания']
                )
                db.add(customer)

        db.commit()
        print("Клиенты успешно импортированы!")

        # Импорт заказов
        print("Импорт заказов...")
        try:
            with open('book_orders.csv', 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Получаем ID клиента по имени
                    customer = db.query(Customer).filter(
                        Customer.full_name == row['ФИО_клиента']
                    ).first()

                    if customer:
                        order = Order(
                            customer_id=customer.id,
                            order_date=datetime.strptime(row['Дата_заказа'], '%Y-%m-%d'),
                            description=f"{row['Название_книги']} - {row['Автор']}",
                            amount=float(row['Общая_сумма'])
                        )
                        db.add(order)

            db.commit()
            print("Заказы успешно импортированы!")
        except FileNotFoundError:
            print("book_orders.csv не найден, пропускаем импорт заказов.")

    except Exception as e:
        print(f"Ошибка при импорте данных: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
    import_sample_data()
