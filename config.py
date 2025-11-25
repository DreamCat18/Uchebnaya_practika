import os

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///./customer_db.db'
)
