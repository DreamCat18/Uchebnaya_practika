import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, date
import logging

class CustomerManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Management System")
        self.root.geometry("1200x700")
        
        self.setup_database()
        self.create_widgets()
        self.load_customers()
    
    def setup_database(self):
        """Настройка базы данных"""
        # Здесь должна быть ваша реализация подключения к БД
        # Для примера используем временное хранилище
        self.customers = []
        self.next_id = 1
    
    def create_widgets(self):
        """Создание интерфейса"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель поиска и кнопок
        self.create_control_panel(main_frame)
        
        # Список клиентов
        self.create_customer_list(main_frame)
    
    def create_control_panel(self, parent):
        """Панель управления"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки действий
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(btn_frame, text="Add Customer", 
                  command=self.add_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Export CSV", 
                  command=self.export_to_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refresh", 
                  command=self.load_customers).pack(side=tk.LEFT, padx=2)
        
        # Поиск
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_customers())
        
        ttk.Button(search_frame, text="Search", 
                  command=self.search_customers).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Clear", 
                  command=self.clear_search).pack(side=tk.LEFT, padx=2)
    
    def create_customer_list(self, parent):
        """Список клиентов с таблицей"""
        # Фрейм для таблицы
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создание таблицы
        columns = ('ID', 'Full Name', 'Email', 'Phone', 'Registration Date', 'Notes')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Настройка колонок
        column_widths = {
            'ID': 50,
            'Full Name': 200,
            'Email': 150,
            'Phone': 120,
            'Registration Date': 120,
            'Notes': 250
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Контекстное меню
        self.create_context_menu()
        
        # Привязка событий
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def create_context_menu(self):
        """Создание контекстного меню"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_selected_customer)
        self.context_menu.add_command(label="Delete", command=self.delete_selected_customer)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Details", command=self.view_customer_details)
    
    def add_customer(self):
        """Добавление нового клиента"""
        dialog = AddCustomerDialog(self.root)
        self.root.wait_window(dialog)
        
        if dialog.result:
            customer_data = dialog.result
            customer_data['id'] = self.next_id
            self.next_id += 1
            customer_data['registration_date'] = date.today()
            
            self.customers.append(customer_data)
            self.load_customers()
            
            messagebox.showinfo("Success", "Customer added successfully!")
    
    def edit_customer(self, customer_id):
        """Редактирование клиента"""
        customer = self.find_customer_by_id(customer_id)
        if customer:
            dialog = EditCustomerDialog(self.root, customer)
            self.root.wait_window(dialog)
            
            if dialog.result:
                # Обновление данных клиента
                index = self.customers.index(customer)
                self.customers[index].update(dialog.result)
                self.load_customers()
                
                messagebox.showinfo("Success", "Customer updated successfully!")
        else:
            messagebox.showerror("Error", "Customer not found!")
    
    def delete_customer(self, customer_id):
        """Удаление клиента"""
        customer = self.find_customer_by_id(customer_id)
        if customer:
            customer_name = customer.get('full_name', 'Unknown')
            
            confirm = messagebox.askyesno(
                "Delete Customer", 
                f"Are you sure you want to delete {customer_name}?",
                icon='warning'
            )
            
            if confirm:
                self.customers = [c for c in self.customers if c['id'] != customer_id]
                self.load_customers()
                messagebox.showinfo("Success", "Customer deleted successfully!")
        else:
            messagebox.showerror("Error", "Customer not found!")
    
    def search_customers(self):
        """Поиск клиентов"""
        query = self.search_entry.get().strip().lower()
        
        if not query:
            self.load_customers()
            return
        
        filtered_customers = []
        for customer in self.customers:
            # Поиск по имени, email, телефону
            name_match = query in customer.get('full_name', '').lower()
            email_match = query in customer.get('email', '').lower()
            phone_match = query in customer.get('phone', '').lower()
            notes_match = query in customer.get('notes', '').lower()
            
            if name_match or email_match or phone_match or notes_match:
                filtered_customers.append(customer)
        
        self.display_customers(filtered_customers)
    
    def load_customers(self):
        """Загрузка всех клиентов"""
        # В реальном приложении здесь будет загрузка из БД
        # Для демонстрации используем тестовые данные если список пуст
        if not self.customers:
            self.create_sample_data()
        
        self.display_customers(self.customers)
    
    def display_customers(self, customers):
        """Отображение клиентов в таблице"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение данными
        for customer in customers:
            self.tree.insert('', tk.END, values=(
                customer['id'],
                customer.get('full_name', ''),
                customer.get('email', ''),
                customer.get('phone', ''),
                customer.get('registration_date', ''),
                customer.get('notes', '')[:50] + '...' if customer.get('notes', '') and len(customer.get('notes', '')) > 50 else customer.get('notes', '')
            ))
    
    def export_to_csv(self):
        """Экспорт данных в CSV"""
        if not self.customers:
            messagebox.showwarning("Warning", "No customers to export!")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Customers to CSV"
            )
            
            if file_path:
                # Создание DataFrame
                df = pd.DataFrame([{
                    'ID': c['id'],
                    'Full Name': c.get('full_name', ''),
                    'Email': c.get('email', ''),
                    'Phone': c.get('phone', ''),
                    'Registration Date': c.get('registration_date', ''),
                    'Notes': c.get('notes', '')
                } for c in self.customers])
                
                # Сохранение в CSV
                df.to_csv(file_path, index=False, encoding='utf-8')
                
                messagebox.showinfo("Success", f"Customers exported to:\n{file_path}")
        
        except Exception as e:
            logging.error(f"Export error: {e}")
            messagebox.showerror("Error", f"Failed to export: {e}")
    
    # Вспомогательные методы
    def find_customer_by_id(self, customer_id):
        """Поиск клиента по ID"""
        for customer in self.customers:
            if customer['id'] == customer_id:
                return customer
        return None
    
    def clear_search(self):
        """Очистка поиска"""
        self.search_entry.delete(0, tk.END)
        self.load_customers()
    
    def on_double_click(self, event):
        """Обработка двойного клика"""
        selection = self.tree.selection()
        if selection:
            customer_id = self.tree.item(selection[0])['values'][0]
            self.edit_customer(customer_id)
    
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        selection = self.tree.identify_row(event.y)
        if selection:
            self.tree.selection_set(selection)
            self.context_menu.post(event.x_root, event.y_root)
    
    def edit_selected_customer(self):
        """Редактирование выбранного клиента"""
        selection = self.tree.selection()
        if selection:
            customer_id = self.tree.item(selection[0])['values'][0]
            self.edit_customer(customer_id)
    
    def delete_selected_customer(self):
        """Удаление выбранного клиента"""
        selection = self.tree.selection()
        if selection:
            customer_id = self.tree.item(selection[0])['values'][0]
            self.delete_customer(customer_id)
    
    def view_customer_details(self):
        """Просмотр деталей клиента"""
        selection = self.tree.selection()
        if selection:
            customer_id = self.tree.item(selection[0])['values'][0]
            customer = self.find_customer_by_id(customer_id)
            
            if customer:
                details = f"""
Customer Details:
----------------
ID: {customer['id']}
Full Name: {customer.get('full_name', 'N/A')}
Email: {customer.get('email', 'N/A')}
Phone: {customer.get('phone', 'N/A')}
Registration Date: {customer.get('registration_date', 'N/A')}
Notes: {customer.get('notes', 'N/A')}
"""
                messagebox.showinfo("Customer Details", details)
    
    def create_sample_data(self):
        """Создание тестовых данных"""
        sample_customers = [
            {
                'id': 1,
                'full_name': 'John Smith',
                'email': 'john.smith@email.com',
                'phone': '+1-555-0101',
                'registration_date': '2024-01-15',
                'notes': 'Regular customer, prefers email communication'
            },
            {
                'id': 2,
                'full_name': 'Maria Garcia',
                'email': 'maria.garcia@email.com',
                'phone': '+1-555-0102',
                'registration_date': '2024-02-20',
                'notes': 'VIP client, special discounts apply'
            },
            {
                'id': 3,
                'full_name': 'David Johnson',
                'email': 'david.johnson@email.com',
                'phone': '+1-555-0103',
                'registration_date': '2024-03-10',
                'notes': 'New customer, requires follow-up'
            }
        ]
        
        self.customers = sample_customers
        self.next_id = 4


# Диалоговые окна
class BaseCustomerDialog:
    """Базовый класс для диалоговых окон"""
    
    def __init__(self, parent, title, customer_data=None):
        self.parent = parent
        self.customer_data = customer_data or {}
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.fill_form()
    
    def create_widgets(self):
        """Создание элементов формы"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поля формы
        ttk.Label(main_frame, text="Full Name:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        
        ttk.Label(main_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(main_frame, width=30)
        self.email_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        ttk.Label(main_frame, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(main_frame, width=30)
        self.phone_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
        
        ttk.Label(main_frame, text="Notes:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.notes_text = tk.Text(main_frame, width=30, height=6)
        self.notes_text.grid(row=3, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", 
                  command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel).pack(side=tk.LEFT, padx=10)
    
    def fill_form(self):
        """Заполнение формы данными"""
        if self.customer_data:
            self.name_entry.insert(0, self.customer_data.get('full_name', ''))
            self.email_entry.insert(0, self.customer_data.get('email', ''))
            self.phone_entry.insert(0, self.customer_data.get('phone', ''))
            self.notes_text.insert('1.0', self.customer_data.get('notes', ''))
    
    def validate_form(self):
        """Валидация формы"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Full Name is required!")
            return False
        return True
    
    def save(self):
        """Сохранение данных"""
        if self.validate_form():
            self.result = {
                'full_name': self.name_entry.get().strip(),
                'email': self.email_entry.get().strip(),
                'phone': self.phone_entry.get().strip(),
                'notes': self.notes_text.get('1.0', tk.END).strip()
            }
            self.dialog.destroy()
    
    def cancel(self):
        """Отмена"""
        self.dialog.destroy()


class AddCustomerDialog(BaseCustomerDialog):
    """Диалог добавления клиента"""
    
    def __init__(self, parent):
        super().__init__(parent, "Add New Customer")


class EditCustomerDialog(BaseCustomerDialog):
    """Диалог редактирования клиента"""
    
    def __init__(self, parent, customer_data):
        super().__init__(parent, "Edit Customer", customer_data)


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CustomerManager(root)
    root.mainloop()