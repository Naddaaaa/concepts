import sqlite3

class Database:
    def __init__(self, db_name="hotel_management.db"):
        self.db_name = db_name
        self.connection = None

    def connect(self):
        """Establish a connection to the SQLite database."""
        self.connection = sqlite3.connect(self.db_name)
        print("Connected to the database.")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Connection closed.")

    def create_tables(self):
        """Create tables for rooms, customers, and bills."""
        query_rooms = """
        CREATE TABLE IF NOT EXISTS rooms (
           roomNumber INTEGER PRIMARY KEY,
           roomType TEXT NOT NULL,
           price REAL NOT NULL,
           availability INTEGER NOT NULL,
           customerID INTEGER,  -- Add this column to link rooms to customers
           check_in_time TEXT,  -- Store check-in time as a string
           check_out_time TEXT, -- Store check-out time as a string
           FOREIGN KEY (customerID) REFERENCES customers(customerID)
        );
        """
    
        query_customers = """
        CREATE TABLE IF NOT EXISTS customers (
           customerID INTEGER PRIMARY KEY AUTOINCREMENT,
           name TEXT NOT NULL,
           contactInfo TEXT NOT NULL,
           paymentMethod TEXT NOT NULL
        );
        """
    
        query_bills = """
        CREATE TABLE IF NOT EXISTS bills (
           billID INTEGER PRIMARY KEY AUTOINCREMENT,
           customerID INTEGER,
           roomNumber INTEGER,
           roomType TEXT,
           duration INTEGER,
           additionalServices TEXT,
           totalAmount REAL,
           paymentMethod TEXT,
           billDate DATE,
           FOREIGN KEY (customerID) REFERENCES customers(customerID),
           FOREIGN KEY (roomNumber) REFERENCES rooms(roomNumber)
        );
        """
        query_reservations="""
        CREATE TABLE IF NOT EXISTS reservations (
            reservationID INTEGER PRIMARY KEY AUTOINCREMENT,
            customerID INTEGER NOT NULL,
            roomNumber INTEGER NOT NULL,
            checkInDate DATE NOT NULL,
            checkOutDate DATE NOT NULL,
            FOREIGN KEY (customerID) REFERENCES customers(customerID),
            FOREIGN KEY (roomNumber) REFERENCES rooms(roomNumber)
        );
        """
    
        self.execute_query(query_rooms)
        self.execute_query(query_customers)
        self.execute_query(query_bills)
        self.execute_query(query_reservations)


    def execute_query(self, query, params=()):
        """Execute a query that does not return data (INSERT, UPDATE, DELETE)."""
        if self.connection is None:
            raise Exception("Database connection is not established. Please call connect() first.")
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor  # Return the cursor so fetch_one and fetch_all can be used

    def fetch_one(self, query, params=()):
        """Fetch one record from the database."""
        if self.connection is None:
            raise Exception("Database connection is not established. Please call connect() first.")
        cursor = self.execute_query(query, params)
        return cursor.fetchone()

    def fetch_all(self, query, params=()):
        """Fetch all records from the database."""
        if self.connection is None:
            raise Exception("Database connection is not established. Please call connect() first.")
        cursor = self.execute_query(query, params)
        return cursor.fetchall()

    def check_availability(self, room_number):
        """Check if a room is available."""
        query = "SELECT availability FROM rooms WHERE roomNumber = ?"
        result = self.fetch_one(query, (room_number,))
        return result and result[0] == 1  # Assuming 1 means available

    def book_room(self, room_number, customer_id):
        """Book a room and link it to a customer."""
        if self.check_availability(room_number):
            query = """
            UPDATE rooms
            SET availability = 0, customerID = ?
            WHERE roomNumber = ?
            """
            self.execute_query(query, (customer_id, room_number))
            print(f"Room {room_number} has been booked for customer {customer_id}.")
        else:
            print(f"Room {room_number} is not available.")
 