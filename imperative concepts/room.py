from datetime import datetime
class Room:
    def __init__(self, db):
        self.db = db

    def add_room(self, room_number, room_type, price):
        query = "INSERT INTO rooms (roomNumber, roomType, price, availability) VALUES (?, ?, ?, 1)"
        self.db.execute_query(query, (room_number, room_type, price))
        print(f"Room {room_number} added successfully.")

    def check_availability(self, room_number, check_in_time, check_out_time):
        """Check if a room is available for the given date range."""
        query = """
        SELECT check_in_time, check_out_time FROM rooms
        WHERE roomNumber = ? AND availability = 0
        """
        result = self.db.fetch_one(query, (room_number,))
    
        if result:
            existing_check_in, existing_check_out = result
            # Check if the requested dates overlap with existing bookings
            if (check_in_time < existing_check_out) and (check_out_time > existing_check_in):
                print(f"Room {room_number} is already booked during this period.")
                return False
        return True


    def book_room(self, room_number, customer_name, check_in_time, check_out_time):
        """Book a room by customer name and link it to the room."""
        # Look up the customer ID by customer name
        query = "SELECT customerID FROM customers WHERE name = ?"
        customer = self.db.fetch_one(query, (customer_name,))
    
        if customer is None:
           print(f"No customer found with the name: {customer_name}")
           return
    
        customer_id = customer[0]  # Get the customer ID

        # Check if the room is available and book it
        if self.check_availability(room_number, check_in_time, check_out_time):
           query = """
           UPDATE rooms
           SET availability = 0, customerID = ?, check_in_time = ?, check_out_time = ?
           WHERE roomNumber = ?
           """
           self.db.execute_query(query, (customer_id, check_in_time, check_out_time, room_number))
           print(f"Room {room_number} has been booked for customer {customer_name} from {check_in_time} to {check_out_time}.")
        else:
           print(f"Room {room_number} is not available.")


    

    def release_room(self, room_number):
        query = "UPDATE rooms SET availability = 1 WHERE roomNumber = ?"
        self.db.execute_query(query, (room_number,))
        print(f"Room {room_number} has been released.")

    def show_rooms(self):
        query = "SELECT roomNumber, roomType, price, availability FROM rooms"
        rooms = self.db.execute_query(query).fetchall()
        print("Rooms:")
        for room in rooms:
            status = "Available" if room[3] == 1 else "Booked"
            print(f"Room {room[0]} ({room[1]}): ${room[2]} - {status}")

    # Get room details by room number (for billing or other operations)
    def get_room_details(self, room_number):
        """Get room details (including customer ID) based on room number."""
        query = "SELECT roomNumber, roomType, customerID FROM rooms WHERE roomNumber = ?"
        result = self.db.fetch_one(query, (room_number,))
        if result:
            return {
                "room_number": result[0],
                "room_type": result[1],
                "customer_id": result[2]
            }
        else:
            return None
