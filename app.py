# TODO: Implement add customer
        pass

    def edit_customer(self, customer_id):
        # TODO: Implement edit customer
        pass

    def delete_customer(self, customer_id):
        # TODO: Implement delete customer
        pass

    def search_customers(self):
        # TODO: Implement search
        pass

    def load_customers(self):
        # TODO: Implement load customers
        pass

    def export_to_csv(self):
        # TODO: Implement CSV export
        pass

    def add_customer(self):
        dialog = AddCustomerDialog(self)
        self.wait_window(dialog)
        self.load_customers()

    def edit_customer(self, customer_id):
        customer = self.session.query(Customer).filter_by(id=customer_id).first()
        if customer:
            dialog = EditCustomerDialog(self, customer)
            self.wait_window(dialog)
            self.load_customers()

    def delete_customer(self, customer_id):
        customer = self.session.query(Customer).filter_by(id=customer_id).first()
        if customer:
            confirm = messagebox.askyesno("Delete Customer", f"Are you sure you want to delete {customer.full_name}?")
            if confirm:
                self.session.delete(customer)
                self.session.commit()
                self.load_customers()

    def search_customers(self):
        query = self.search_entry.get().strip()
        if query:
            customers = self.session.query(Customer).filter(
                (Customer.full_name.ilike(f'%{query}%')) | (Customer.email.ilike(f'%{query}%'))
            ).all()
        else:
            customers = self.session.query(Customer).all()
        self.display_customers(customers)

    def load_customers(self):
        customers = self.session.query(Customer).all()
        self.display_customers(customers)

    def display_customers(self, customers):
        # Clear existing customer frames
        for widget in self.customer_list_frame.winfo_children():
            widget.destroy()

        for customer in customers:
            customer_frame = CTkFrame(self.customer_list_frame)
            customer_frame.pack(fill="x", padx=5, pady=2)

            info_text = f"ID: {customer.id} | Name: {customer.full_name} | Email: {customer.email} | Phone: {customer.phone} | Reg: {customer.registration_date}"
            info_label = CTkLabel(customer_frame, text=info_text, anchor="w")
            info_label.pack(side="left", fill="x", expand=True, padx=5, pady=5)

            edit_button = CTkButton(customer_frame, text="Edit", command=lambda cid=customer.id: self.edit_customer(cid))
            edit_button.pack(side="right", padx=2)

            delete_button = CTkButton(customer_frame, text="Delete", command=lambda cid=customer.id: self.delete_customer(cid))
            delete_button.pack(side="right", padx=2)

    def export_to_csv(self):
        customers = self.session.query(Customer).all()
        df = pd.DataFrame([{
            'ID': c.id,
            'ФИО': c.full_name,
            'Контактная информация': c.contact_info,
            'Email': c.email,
            'Телефон': c.phone,
            'Дата регистрации': c.registration_date,
            'Примечания': c.notes
        } for c in customers])
        df.to_csv('customers_export.csv', index=False)
        messagebox.showinfo("Export", "Customers exported to customers_export.csv")
