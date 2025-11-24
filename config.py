# Configuration for the customer accounting module
import os

# Database URL - update with your PostgreSQL credentials
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/customer_db')
