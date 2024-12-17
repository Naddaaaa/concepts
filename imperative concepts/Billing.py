class Billing:
    def __init__(self, db):
        self.db = db

    def calculate_room_charge(self, room_type, duration):
        room_rates = {
            "single": 100,
            "double": 150,
            "suite": 250
        }
        return room_rates.get(room_type.lower(), 0) * duration

    def calculate_additional_services(self, services):
        service_rates = {
            "meals": 20,  # Changed to lowercase
            "laundry": 15
        }
        total_service_cost = 0
        if services:
           for service in services:
            total_service_cost += service_rates.get(service.strip().lower(), 0)  # Normalize service input
        return total_service_cost


    def apply_discounts_and_taxes(self, total_amount, discount_percentage=0, tax_percentage=10):
        discounted_amount = total_amount - (total_amount * discount_percentage / 100)
        final_amount = discounted_amount + (discounted_amount * tax_percentage / 100)
        return final_amount

    def generate_bill(self, customer_id, room_number, room_type, duration, services, discount_percentage=0):
        room_charge = self.calculate_room_charge(room_type, duration)
        service_charge = self.calculate_additional_services(services)
        total_amount = room_charge + service_charge
        final_amount = self.apply_discounts_and_taxes(total_amount, discount_percentage)
    
        print(f"Room charge: {room_charge}")
        print(f"Service charge: {service_charge}")
        print(f"Total amount before discount: {total_amount}")
        print(f"Final amount after discount: {final_amount}")
    
        query = """
        INSERT INTO bills (customerID, roomNumber, roomType, duration, additionalServices, totalAmount, paymentMethod)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute_query(query, (customer_id, room_number, room_type, duration, ', '.join(services), final_amount, "Pending"))
        print(f"Bill generated successfully. Total Amount: ${final_amount:.2f}")
        return final_amount


    def process_payment(self, bill_id, payment_method, amount_paid):
        bill = self.db.fetch_one("SELECT * FROM bills WHERE billID = ?", (bill_id,))
        if not bill:
            print(f"No bill found with ID {bill_id}.")
            return

        total_amount = bill[6]
        if amount_paid >= total_amount:
            self.db.execute_query("UPDATE bills SET paymentMethod = ?, totalAmount = ? WHERE billID = ?", (payment_method, amount_paid, bill_id))
            print(f"Payment of ${amount_paid:.2f} processed successfully.")
        else:
            print("Insufficient payment. Payment not processed.")
