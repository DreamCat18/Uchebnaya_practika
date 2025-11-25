# quick_init.py - Быстрая инициализация базы данных
from database import engine, Base
from models import Customer, Order

print("Создание таблиц в базе данных...")
Base.metadata.create_all(bind=engine)
print("Готово! Теперь можно запускать gui.py")
