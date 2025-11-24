import customtkinter as ctk
from tkinter import ttk, messagebox, Toplevel
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


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Управление клиентами и заказами")
        self.geometry("1000x700")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add("Клиенты")
        self.tabview.add("Заказы")
        self.tabview.add("Отчеты")

        self.setup_customers_tab()
        self.setup_orders_tab()
        self.setup_reports_tab()

    def setup_customers_tab(self):
        tab = self.tabview.tab("Клиенты")

        # Search frame
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(search_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5)
        self.customer_name_entry = ctk.CTkEntry(search_frame)
        self.customer_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(search_frame, text="Контакты:").grid(row=0, column=2, padx=5, pady=5)
        self.customer_contact_entry = ctk.CTkEntry(search_frame)
        self.customer_contact_entry.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(search_frame, text="Примечания:").grid(row=1, column=0, padx=5, pady=5)
        self.customer_notes_entry = ctk.CTkEntry(search_frame)
        self.customer_notes_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(search_frame, text="Нач. дата (ГГГГ-ММ-ДД):").grid(row=1, column=2, padx=5, pady=5)
        self.customer_start_date_entry = ctk.CTkEntry(search_frame)
        self.customer_start_date_entry.grid(row=1, column=3, padx=5, pady=5)

        ctk.CTkLabel(search_frame, text="Кон. дата (ГГГГ-ММ-ДД):").grid(row=1, column=4, padx=5, pady=5)
        self.customer_end_date_entry = ctk.CTkEntry(search_frame)
        self.customer_end_date_entry.grid(row=1, column=5, padx=5, pady=5)

        ctk.CTkButton(search_frame, text="Поиск", command=self.search_customers).grid(row=0, column=4, padx=5, pady=5)
        ctk.CTkButton(search_frame, text="Очистить", command=self.clear_customer_search).grid(row=1, column=5, padx=5, pady=5)

        # List frame
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.customers_tree = ttk.Treeview(list_frame, columns=("ID", "Имя", "Контакты", "Дата регистрации", "Примечания"), show="headings", height=15)
        self.customers_tree.heading("ID", text="ID")
        self.customers_tree.heading("Имя", text="Имя")
        self.customers_tree.heading("Контакты", text="Контакты")
        self.customers_tree.heading("Дата регистрации", text="Дата регистрации")
        self.customers_tree.heading("Примечания", text="Примечания")
        self.customers_tree.column("ID", width=50)
        self.customers_tree.column("Имя", width=150)
        self.customers_tree.column("Контакты", width=150)
        self.customers_tree.column("Дата регистрации", width=120)
        self.customers_tree.column("Примечания", width=200)

        scrollbar = ctk.CTkScrollbar(list_frame, command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        self.customers_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(button_frame, text="Добавить клиента", command=self.add_customer).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Редактировать клиента", command=self.edit_customer).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Удалить клиента", command=self.delete_customer).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Обновить список", command=self.load_customers).pack(side="left", padx=5)

        self.load_customers()

    def load_customers(self, customers=None):
        for i in self.customers_tree.get_children():
            self.customers_tree.delete(i)
        db: Session = next(get_db())
        if customers is None:
            customers = get_customers(db)
        for c in customers:
            self.customers_tree.insert("", "end", values=(c.id, c.full_name, c.contact_info, c.registration_date.strftime('%Y-%m-%d'), c.notes or ""))
        db.close()

    def search_customers(self):
        db: Session = next(get_db())
        results = []
        name = self.customer_name_entry.get().strip()
        contact = self.customer_contact_entry.get().strip()
        notes = self.customer_notes_entry.get().strip()
        start_date_str = self.customer_start_date_entry.get().strip()
        end_date_str = self.customer_end_date_entry.get().strip()

        if name:
            results = search_customers_by_name(db, name)
        elif contact:
            results = search_customers_by_contact(db, contact)
        elif notes:
            results = search_customers_by_notes(db, notes)
        elif start_date_str and end_date_str:
            try:
                start = datetime.strptime(start_date_str, '%Y-%m-%d')
                end = datetime.strptime(end_date_str, '%Y-%m-%d')
                results = search_customers_by_date_range(db, start, end)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
                db.close()
                return
        else:
            results = get_customers(db)
        db.close()
        self.load_customers(results)

    def clear_customer_search(self):
        self.customer_name_entry.delete(0, 'end')
        self.customer_contact_entry.delete(0, 'end')
        self.customer_notes_entry.delete(0, 'end')
        self.customer_start_date_entry.delete(0, 'end')
        self.customer_end_date_entry.delete(0, 'end')
        self.load_customers()

    def add_customer(self):
        dialog = CustomerDialog(self, "Добавить клиента")
        if dialog.result:
            db: Session = next(get_db())
            try:
                customer = create_customer(db, dialog.result['name'], dialog.result['contact'], dialog.result['notes'])
                messagebox.showinfo("Успех", f"Клиент добавлен с ID: {customer.id}")
                self.load_customers()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
            finally:
                db.close()

    def edit_customer(self):
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента для редактирования")
            return
        item = self.customers_tree.item(selected[0])
        values = item['values']
        customer_id = values[0]
        db: Session = next(get_db())
        customer = get_customer_by_id(db, customer_id)
        db.close()
        if not customer:
            messagebox.showerror("Ошибка", "Клиент не найден")
            return
        dialog = CustomerDialog(self, "Редактировать клиента", customer)
        if dialog.result:
            db: Session = next(get_db())
            try:
                update_customer(db, customer_id, dialog.result['name'], dialog.result['contact'], dialog.result['notes'])
                messagebox.showinfo("Успех", "Данные клиента обновлены")
                self.load_customers()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
            finally:
                db.close()

    def delete_customer(self):
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента для удаления")
            return
        item = self.customers_tree.item(selected[0])
        values = item['values']
        customer_id = values[0]
        if messagebox.askyesno("Подтверждение", "Удалить клиента?"):
            db: Session = next(get_db())
            try:
                if delete_customer(db, customer_id):
                    messagebox.showinfo("Успех", "Клиент удален")
                    self.load_customers()
                else:
                    messagebox.showerror("Ошибка", "Клиент не найден")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
            finally:
                db.close()

    def setup_orders_tab(self):
        tab = self.tabview.tab("Заказы")

        # List frame
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.orders_tree = ttk.Treeview(list_frame, columns=("ID", "Клиент", "Описание", "Сумма", "Дата"), show="headings", height=15)
        self.orders_tree.heading("ID", text="ID")
        self.orders_tree.heading("Клиент", text="Клиент")
        self.orders_tree.heading("Описание", text="Описание")
        self.orders_tree.heading("Сумма", text="Сумма")
        self.orders_tree.heading("Дата", text="Дата")
        self.orders_tree.column("ID", width=50)
        self.orders_tree.column("Клиент", width=150)
        self.orders_tree.column("Описание", width=200)
        self.orders_tree.column("Сумма", width=100)
        self.orders_tree.column("Дата", width=120)

        scrollbar = ctk.CTkScrollbar(list_frame, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        self.orders_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(button_frame, text="Добавить заказ", command=self.add_order).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Редактировать заказ", command=self.edit_order).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Удалить заказ", command=self.delete_order).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Обновить список", command=self.load_orders).pack(side="left", padx=5)

        self.load_orders()

    def load_orders(self):
        for i in self.orders_tree.get_children():
            self.orders_tree.delete(i)
        db: Session = next(get_db())
        orders = get_orders(db)
        for o in orders:
            self.orders_tree.insert("", "end", values=(o.id, o.customer.full_name, o.description, o.amount, o.order_date.strftime('%Y-%m-%d')))
        db.close()

    def add_order(self):
        dialog = OrderDialog(self, "Добавить заказ")
        if dialog.result:
            db: Session = next(get_db())
            try:
                order = create_order(db, dialog.result['customer_id'], dialog.result['description'], dialog.result['amount'])
                messagebox.showinfo("Успех", f"Заказ добавлен с ID: {order.id}")
                self.load_orders()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
            finally:
                db.close()

    def edit_order(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ для редактирования")
            return
        item = self.orders_tree.item(selected[0])
        values = item['values']
        order_id = values[0]
        db: Session = next(get_db())
        order = get_order_by_id(db, order_id)
        db.close()
        if not order:
            messagebox.showerror("Ошибка", "Заказ не найден")
            return
        dialog = OrderDialog(self, "Редактировать заказ", order)
        if dialog.result:
            db: Session = next(get_db())
            try:
                update_order(db, order_id, dialog.result['description'], dialog.result['amount'])
                messagebox.showinfo("Успех", "Заказ обновлен")
                self.load_orders()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
            finally:
                db.close()

    def delete_order(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ для удаления")
            return
        item = self.orders_tree.item(selected[0])
        values = item['values']
        order_id = values[0]
        if messagebox.askyesno("Подтверждение", "Удалить заказ?"):
            db: Session = next(get_db())
            try:
                if delete_order(db, order_id):
                    messagebox.showinfo("Успех", "Заказ удален")
                    self.load_orders()
                else:
                    messagebox.showerror("Ошибка", "Заказ не найден")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
            finally:
                db.close()

    def setup_reports_tab(self):
        tab = self.tabview.tab("Отчеты")

        frame = ctk.CTkFrame(tab)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkButton(frame, text="Отчет по клиентам", command=self.generate_customer_report).pack(pady=10)
        ctk.CTkButton(frame, text="Отчет по заказам", command=self.generate_orders_report).pack(pady=10)

        # For date report
        date_frame = ctk.CTkFrame(frame)
        date_frame.pack(pady=10, fill="x")
        ctk.CTkLabel(date_frame, text="Нач. дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5)
        self.report_start_date = ctk.CTkEntry(date_frame)
        self.report_start_date.grid(row=0, column=1, padx=5)
        ctk.CTkLabel(date_frame, text="Кон. дата (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5)
        self.report_end_date = ctk.CTkEntry(date_frame)
        self.report_end_date.grid(row=0, column=3, padx=5)
        ctk.CTkButton(date_frame, text="Отчет по клиентам за период", command=self.generate_customers_by_date_report).grid(row=0, column=4, padx=5)

    def generate_customer_report(self):
        db: Session = next(get_db())
        try:
            generate_customer_report(db)
            messagebox.showinfo("Успех", "Отчет по клиентам сгенерирован: customer_report.csv")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            db.close()

    def generate_orders_report(self):
        db: Session = next(get_db())
        try:
            generate_orders_report(db)
            messagebox.showinfo("Успех", "Отчет по заказам сгенерирован: orders_report.csv")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            db.close()

    def generate_customers_by_date_report(self):
        start_str = self.report_start_date.get().strip()
        end_str = self.report_end_date.get().strip()
        if not start_str or not end_str:
            messagebox.showerror("Ошибка", "Введите начальную и конечную даты")
            return
        try:
            start = datetime.strptime(start_str, '%Y-%m-%d')
            end = datetime.strptime(end_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        db: Session = next(get_db())
        try:
            generate_customers_by_date_report(db, start, end)
            messagebox.showinfo("Успех", "Отчет по клиентам за период сгенерирован: customers_by_date_report.csv")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            db.close()


class CustomerDialog(Toplevel):
    def __init__(self, parent, title, customer=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x300")
        self.resizable(False, False)
        self.result = None

        ctk.CTkLabel(self, text="Имя:").pack(pady=5)
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Контакты:").pack(pady=5)
        self.contact_entry = ctk.CTkEntry(self)
        self.contact_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Примечания:").pack(pady=5)
        self.notes_entry = ctk.CTkEntry(self)
        self.notes_entry.pack(pady=5)

        if customer:
            self.name_entry.insert(0, customer.full_name)
            self.contact_entry.insert(0, customer.contact_info)
            self.notes_entry.insert(0, customer.notes or "")

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="OK", command=self.ok).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Отмена", command=self.cancel).pack(side="right", padx=10)

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def ok(self):
        name = self.name_entry.get().strip()
        contact = self.contact_entry.get().strip()
        notes = self.notes_entry.get().strip()
        if not name or not contact:
            messagebox.showerror("Ошибка", "Имя и контакты обязательны")
            return
        self.result = {'name': name, 'contact': contact, 'notes': notes}
        self.destroy()

    def cancel(self):
        self.destroy()


class OrderDialog(Toplevel):
    def __init__(self, parent, title, order=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x250")
        self.resizable(False, False)
        self.result = None

        ctk.CTkLabel(self, text="ID клиента:").pack(pady=5)
        self.customer_id_entry = ctk.CTkEntry(self)
        self.customer_id_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Описание:").pack(pady=5)
        self.description_entry = ctk.CTkEntry(self)
        self.description_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Сумма:").pack(pady=5)
        self.amount_entry = ctk.CTkEntry(self)
        self.amount_entry.pack(pady=5)

        if order:
            self.customer_id_entry.insert(0, str(order.customer_id))
            self.description_entry.insert(0, order.description)
            self.amount_entry.insert(0, str(order.amount))

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="OK", command=self.ok).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Отмена", command=self.cancel).pack(side="right", padx=10)

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def ok(self):
        try:
            customer_id = int(self.customer_id_entry.get().strip())
            description = self.description_entry.get().strip()
            amount = float(self.amount_entry.get().strip())
            if not description:
                raise ValueError
            self.result = {'customer_id': customer_id, 'description': description, 'amount': amount}
            self.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Неверные данные")

    def cancel(self):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
