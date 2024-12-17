from datetime import datetime

class Reservation:
    def __init__(self, db, room_manager):
        self.db = db
        self.room_manager = room_manager

    def make_reservation(self, customer_name, room_number, check_in_date, check_out_date):
        # Check if customer exists
        customer_query = "SELECT * FROM customers WHERE name = ?"
        customer_exists = self.db.fetch_one(customer_query, (customer_name,))

        if not customer_exists:
           print(f"Customer {customer_name} not found.")
           return

        # Check room availability
        if self.room_manager.check_availability(room_number, check_in_date, check_out_date):
           query = """
               INSERT INTO reservations (customerID, roomNumber, checkInDate, checkOutDate)
               VALUES (
                   (SELECT customerID FROM customers WHERE name = ?),
                   ?, ?, ?
              )
           """
           self.db.execute_query(query, (customer_name, room_number, check_in_date, check_out_date))
           self.room_manager.book_room(room_number, customer_name, check_in_date, check_out_date)
           print(f"Reservation for {customer_name} in room {room_number} from {check_in_date} to {check_out_date} confirmed.")
        else:
          print(f"Room {room_number} is not available for reservation.")


    def check_in(self, room_number):
        query = """
            DELETE FROM reservations WHERE roomNumber = ? AND date(checkInDate) <= date('now')
        """
        self.db.execute_query(query, (room_number,))
        self.room_manager.book_room(room_number)
        print(f"Guest checked into room {room_number}.")

    def check_out(self, room_number):
        self.room_manager.release_room(room_number)
        print(f"Guest checked out of room {room_number}.")
