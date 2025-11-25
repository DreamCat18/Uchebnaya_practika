from crud import read_customers_from_csv


def search_customers_by_name(db, name):
    customers = read_customers_from_csv()
    return [c for c in customers if name.lower() in c.full_name.lower()]


def search_customers_by_contact(db, contact):
    customers = read_customers_from_csv()
    return [c for c in customers if contact.lower() in
            c.contact_info.lower()]


def search_customers_by_notes(db, notes):
    customers = read_customers_from_csv()
    return [c for c in customers if c.notes and notes.lower() in
            c.notes.lower()]


def search_customers_by_date_range(db, start_date, end_date):
    customers = read_customers_from_csv()
    return [c for c in customers if start_date <= c.registration_date <=
            end_date]
