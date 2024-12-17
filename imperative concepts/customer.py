class CustomerManager:
    def __init__(self, db):
        self.db = db

    def add_customer(self, name, contact_info, payment_method):
        query = """
        INSERT INTO customers (name, contactInfo, paymentMethod)
        VALUES (?, ?, ?)
        """
        self.db.execute_query(query, (name, contact_info, payment_method))
        print("Customer added successfully.")

    def search_customer(self, name):
        query = "SELECT * FROM customers WHERE name LIKE ?"
        customers = self.db.fetch_all(query, ('%' + name + '%',))
        if customers:
            for customer in customers:
                print(f"ID: {customer[0]}, Name: {customer[1]}, Contact: {customer[2]}, Payment: {customer[3]}")
        else:
            print("No customers found.")

    def update_customer(self, customer_name, name=None, contact_info=None, payment_method=None):
        # Query to get customer ID based on customer name
        query = "SELECT customerID FROM customers WHERE name = ?"
        customer = self.db.fetch_one(query, (customer_name,))
    
        if not customer:
            print(f"No customer found with the name {customer_name}.")
            return
    
        customer_id = customer[0]
    
        # Now, update the customer details using the customer_id
        update_query = """
        UPDATE customers
        SET name = COALESCE(?, name),
            contactInfo = COALESCE(?, contactInfo),
            paymentMethod = COALESCE(?, paymentMethod)
         WHERE customerID = ?
         """
        self.db.execute_query(update_query, (name, contact_info, payment_method, customer_id))
        print(f"Customer with name {customer_name} updated successfully.")
