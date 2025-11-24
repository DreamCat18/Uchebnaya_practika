import argparse
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from crud import (
    create_customer,
    get_customers,
    get_customer_by_id,
    update_customer,
    delete_customer,
    create_order,
    get_orders,
    get_order_by_id,
    update_order,
    delete_order
)
from search import (
    search_customers_by_name, search_customers_by_contact,
    search_customers_by_date_range, search_customers_by_notes
)
from reports import (
    generate_customer_report,
    generate_orders_report,
    generate_customers_by_date_report
)


def main():
    """Основная функция консольного интерфейса."""
    parser = argparse.ArgumentParser(description='Модуль учета клиентов')
    subparsers = parser.add_subparsers(
        dest='command',
        help='Доступные команды'
    )

    # Команды для работы с клиентами
    customer_parser = subparsers.add_parser(
        'customer',
        help='Операции с клиентами'
    )
    customer_subparsers = customer_parser.add_subparsers(dest='action')

    # Добавление клиента
    add_customer_parser = customer_subparsers.add_parser(
        'add',
        help='Добавить нового клиента'
    )
    add_customer_parser.add_argument(
        '--name',
        required=True,
        help='Полное имя'
    )
    add_customer_parser.add_argument(
        '--contact',
        required=True,
        help='Контактная информация'
    )
    add_customer_parser.add_argument('--notes', help='Примечания')

    # Список клиентов
    customer_subparsers.add_parser('list', help='Показать всех клиентов')

    # Получение клиента по ID
    get_customer_parser = customer_subparsers.add_parser(
        'get',
        help='Найти клиента по ID'
    )
    get_customer_parser.add_argument(
        '--id',
        type=int,
        required=True,
        help='ID клиента'
    )

    # Обновление клиента
    update_customer_parser = customer_subparsers.add_parser(
        'update',
        help='Обновить данные клиента'
    )
    update_customer_parser.add_argument(
        '--id',
        type=int,
        required=True,
        help='ID клиента'
    )
    update_customer_parser.add_argument('--name', help='Новое полное имя')
    update_customer_parser.add_argument(
        '--contact',
        help='Новая контактная информация'
    )
    update_customer_parser.add_argument('--notes', help='Новые примечания')

    # Удаление клиента
    delete_customer_parser = customer_subparsers.add_parser(
        'delete',
        help='Удалить клиента'
    )
    delete_customer_parser.add_argument(
        '--id',
        type=int,
        required=True,
        help='ID клиента'
    )

    # Поиск клиентов
    search_customer_parser = customer_subparsers.add_parser(
        'search',
        help='Поиск клиентов'
    )
    search_customer_parser.add_argument('--name', help='Поиск по имени')
    search_customer_parser.add_argument('--contact', help='Поиск по контактам')
    search_customer_parser.add_argument(
        '--start-date',
        help='Начальная дата регистрации (ГГГГ-ММ-ДД)'
    )
    search_customer_parser.add_argument(
        '--end-date',
        help='Конечная дата регистрации (ГГГГ-ММ-ДД)'
    )
    search_customer_parser.add_argument(
        '--notes',
        help='Поиск по ключевому слову в примечаниях'
    )

    # Команды для работы с заказами
    order_parser = subparsers.add_parser('order', help='Операции с заказами')
    order_subparsers = order_parser.add_subparsers(dest='action')

    # Добавление заказа
    add_order_parser = order_subparsers.add_parser(
        'add',
        help='Добавить новый заказ'
    )
    add_order_parser.add_argument(
        '--customer-id',
        type=int,
        required=True,
        help='ID клиента'
    )
    add_order_parser.add_argument(
        '--description',
        required=True,
        help='Описание заказа'
    )
    add_order_parser.add_argument(
        '--amount',
        type=float,
        required=True,
        help='Сумма заказа'
    )

    # Список заказов
    order_subparsers.add_parser('list', help='Показать все заказы')

    # Получение заказа по ID
    get_order_parser = order_subparsers.add_parser(
        'get',
        help='Найти заказ по ID'
    )
    get_order_parser.add_argument(
        '--id',
        type=int,
        required=True,
        help='ID заказа'
    )

    # Обновление заказа
    update_order_parser = order_subparsers.add_parser(
        'update',
        help='Обновить заказ'
    )
    update_order_parser.add_argument(
        '--id',
        type=int,
        required=True,
        help='ID заказа'
    )
    update_order_parser.add_argument('--description', help='Новое описание')
    update_order_parser.add_argument(
        '--amount',
        type=float,
        help='Новая сумма'
    )

    # Удаление заказа
    delete_order_parser = order_subparsers.add_parser(
        'delete',
        help='Удалить заказ'
    )
    delete_order_parser.add_argument(
        '--id',
        type=int,
        required=True,
        help='ID заказа'
    )

    # Команды для отчетов
    report_parser = subparsers.add_parser('report', help='Генерация отчетов')
    report_subparsers = report_parser.add_subparsers(dest='action')

    # Отчет по клиентам
    report_subparsers.add_parser(
        'customers',
        help='Сгенерировать отчет по клиентам'
    )

    # Отчет по заказам
    report_subparsers.add_parser(
        'orders',
        help='Сгенерировать отчет по заказам'
    )

    # Отчет по клиентам по дате
    date_report_parser = report_subparsers.add_parser(
        'customers-by-date',
        help='Сгенерировать отчет по клиентам за период'
    )
    date_report_parser.add_argument(
        '--start-date',
        required=True,
        help='Начальная дата (ГГГГ-ММ-ДД)'
    )
    date_report_parser.add_argument(
        '--end-date',
        required=True,
        help='Конечная дата (ГГГГ-ММ-ДД)'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    db: Session = next(get_db())

    try:
        if args.command == 'customer':
            if args.action == 'add':
                customer = create_customer(
                    db,
                    args.name,
                    args.contact,
                    args.notes
                )
                print(f'Клиент добавлен с ID: {customer.id}')
            elif args.action == 'list':
                customers = get_customers(db)
                for c in customers:
                    print(
                        f'ID: {c.id},'
                        f'Имя: {c.full_name},'
                        f'Контакты: {c.contact_info}'
                    )
            elif args.action == 'get':
                customer = get_customer_by_id(db, args.id)
                if customer:
                    print(
                        f'ID: {customer.id},'
                        f'Имя: {customer.full_name}, '
                        f'Контакты: {customer.contact_info},'
                        f'Примечания: {customer.notes}'
                    )
                else:
                    print('Клиент не найден')
            elif args.action == 'update':
                customer = update_customer(
                    db,
                    args.id,
                    args.name,
                    args.contact,
                    args.notes
                )
                if customer:
                    print('Данные клиента обновлены')
                else:
                    print('Клиент не найден')
            elif args.action == 'delete':
                if delete_customer(db, args.id):
                    print('Клиент удален')
                else:
                    print('Клиент не найден')
            elif args.action == 'search':
                results = []
                if args.name:
                    results = search_customers_by_name(db, args.name)
                elif args.contact:
                    results = search_customers_by_contact(db, args.contact)
                elif args.start_date and args.end_date:
                    start = datetime.strptime(args.start_date, '%Y-%m-%d')
                    end = datetime.strptime(args.end_date, '%Y-%m-%d')
                    results = search_customers_by_date_range(db, start, end)
                elif args.notes:
                    results = search_customers_by_notes(db, args.notes)
                for c in results:
                    print(
                        f'ID: {c.id},'
                        f'Имя: {c.full_name},'
                        f'Контакты: {c.contact_info}'
                    )
        elif args.command == 'order':
            if args.action == 'add':
                order = create_order(
                    db,
                    args.customer_id,
                    args.description,
                    args.amount
                )
                print(f'Заказ добавлен с ID: {order.id}')
            elif args.action == 'list':
                orders = get_orders(db)
                for o in orders:
                    print(
                        f'ID: {o.id},'
                        f'Клиент: {o.customer.full_name},'
                        f'Описание: {o.description},'
                        f'Сумма: {o.amount}'
                    )
            elif args.action == 'get':
                order = get_order_by_id(db, args.id)
                if order:
                    print(
                        f'ID: {order.id},'
                        f'Клиент: {order.customer.full_name},'
                        f'Описание: {order.description},'
                        f'Сумма: {order.amount}'
                    )
                else:
                    print('Заказ не найден')
            elif args.action == 'update':
                order = update_order(
                    db,
                    args.id,
                    args.description,
                    args.amount
                )
                if order:
                    print('Заказ обновлен')
                else:
                    print('Заказ не найден')
            elif args.action == 'delete':
                if delete_order(db, args.id):
                    print('Заказ удален')
                else:
                    print('Заказ не найден')
        elif args.command == 'report':
            if args.action == 'customers':
                generate_customer_report(db)
                print('Отчет по клиентам сгенерирован: customer_report.csv')
            elif args.action == 'orders':
                generate_orders_report(db)
                print('Отчет по заказам сгенерирован: orders_report.csv')
            elif args.action == 'customers-by-date':
                start = datetime.strptime(args.start_date, '%Y-%m-%d')
                end = datetime.strptime(args.end_date, '%Y-%m-%d')
                generate_customers_by_date_report(db, start, end)
                print(
                    'Отчет по клиентам сгенерирован: '
                    'customers_by_date_report.csv'
                )
    except Exception as e:
        print(f'Ошибка: {e}')
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    main()
