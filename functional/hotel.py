import json
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta

# Tuple Immutability: Since rooms is a tuple, every time a new room is added, the entire tuple is recreated 
# by concatenating the new room. This is generally okay,
#  but it might not be optimal for larger data sets because of the overhead of creating a new tuple each time.
# Recommendations:
# Switch from Tuple to List
Room = Dict[str, str | int | bool]
Reservation = Dict[str, str | int | Tuple[str, str]]
Customer = Dict[str, str | int]

# --- JSON UTILITIES ---
def load_from_json(file_name: str) -> Any:
    """Load data from a JSON file."""
    try:
        with open(file_name, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_to_json(file_name: str, data: Any) -> None:
    """Save data to a JSON file, force overwriting."""
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

# --- ROOM MANAGEMENT ---
def create_room(room_number: int, room_type: str, price: int, available: bool) -> Room:
    """Create a new room."""
    return {"roomNumber": room_number, "roomType": room_type, "price": price, "available": available}

def update_room_availability(rooms: Tuple[Room, ...], room_number: int, availability: bool) -> Tuple[Room, ...]:
    """Recursively update room availability."""
    if not rooms:
        return ()
    room = rooms[0]
    if room["roomNumber"] == room_number:
        updated_room = {**room, 'available': availability}
        return (updated_room,) + update_room_availability(rooms[1:], room_number, availability)
    return (room,) + update_room_availability(rooms[1:], room_number, availability)

def check_room_status(rooms: Tuple[Room, ...], room_number: int) -> Optional[Room]:
    """Recursively find room by number."""
    if not rooms:
        return None
    room = rooms[0]
    if room["roomNumber"] == room_number:
        return room
    return check_room_status(rooms[1:], room_number)

def release_room(rooms: Tuple[Room, ...], room_number: int) -> Tuple[Room, ...]:
    """Release a room by making it available."""
    return update_room_availability(rooms, room_number, True)

def check_if_room_exists(rooms: Tuple[Room, ...], room_number: int) -> bool:
    """Recursively check if the room number already exists."""
    if not rooms:
        return False
    room = rooms[0]
    if room["roomNumber"] == room_number:
        return True
    return check_if_room_exists(rooms[1:], room_number)

def is_room_available_for_period(
    rooms: Tuple[Room, ...], 
    room_number: int, 
    start_date: str, 
    end_date: str,
    reservations: Tuple[Reservation, ...]  # Added reservations as a parameter
) -> bool:
    """Check if the room is available during the specified period."""
    
    room = check_room_status(rooms, room_number)
    if room:
        # Recursive function to check if the room is available during the specified dates
        def check_reservations(reservations: Tuple[Reservation, ...]) -> bool:
            if not reservations:
                return True  # Base case: No more reservations, the room is available
            reservation = reservations[0]
            res_start, res_end = reservation["dates"]
            # Check if dates overlap
            if not (end_date < res_start or start_date > res_end):
                return False  # Room is not available
            return check_reservations(reservations[1:])  # Recursive call for next reservation
        
        # Call the recursive function to check availability
        return check_reservations(reservations)
    return False  # If room is not found or not available
def add_reservation(
    reservations: Tuple[Reservation, ...],
    rooms: Tuple[Room, ...],
    reservation: Reservation
) -> Optional[Tuple[Tuple[Reservation, ...], Tuple[Room, ...]]]:
    """Add a reservation if the room is available and if room is not already reserved for that period."""
    room = check_room_status(rooms, reservation["roomNumber"])
    if room:
        customer_name = reservation["customerName"]
        start_date, end_date = reservation["dates"]
        
        if not is_room_available_for_period(rooms, reservation["roomNumber"], start_date, end_date, reservations):
            print(f"Room {reservation['roomNumber']} is not available for the selected dates.")
            return None  # Room is not available for the selected period
        
        # Room is available, so proceed with the reservation
        updated_rooms = update_room_availability(rooms, reservation["roomNumber"], False)
        updated_reservations = reservations + (reservation,)
        return (updated_reservations, updated_rooms)
    print(f"Room {reservation['roomNumber']} is not available.")
    return None  # Room does not exist or is unavailable

# --- RESERVATION SYSTEM ---
def create_reservation(customer_name: str, room_number: int, dates: Tuple[str, str]) -> Reservation:
    """Create a new reservation."""
    return {"customerName": customer_name, "roomNumber": room_number, "dates": dates}

# --- CUSTOMER MANAGEMENT ---
def add_customer(customers: Tuple[Customer, ...], name: str, contact_info: str, payment_method: str) -> Tuple[Customer, ...]:
    """Add a customer."""
    customer = {"name": name, "contactInfo": contact_info, "paymentMethod": payment_method}
    return customers + (customer,)

def search_customer(customers: Tuple[Customer, ...], name: str) -> Optional[Customer]:
    """Recursively search for a customer by name."""
    if not customers:
        return None
    customer = customers[0]
    if customer["name"] == name:
        return customer
    return search_customer(customers[1:], name)

# --- FILTER RESERVATIONS ---
def filter_reservations_by_period(reservations: Tuple[Reservation, ...], start_date: str, end_date: str) -> Tuple[Reservation, ...]:
    """Filter reservations by a date range."""
    def overlaps(reservation: Reservation) -> bool:
        res_start, res_end = reservation["dates"]
        return not (res_end < start_date or res_start > end_date)

    if not reservations:
        return ()
    reservation = reservations[0]
    if overlaps(reservation):
        return (reservation,) + filter_reservations_by_period(reservations[1:], start_date, end_date)
    return filter_reservations_by_period(reservations[1:], start_date, end_date)

# --- UTILITY FUNCTIONS ---
def generate_bill(reservations, rooms, room_number, days, additional_services, tax_rate, discount):
    """Recursively generate the bill based on reservation details."""
    if not reservations:
        return None  # base case: no more reservations

    reservation = reservations[0]  # Process the first reservation in the list
    if reservation['roomNumber'] == room_number:
        room = check_room_status(rooms, room_number)
        if room:
            room_price = room['price']
            total_cost = (room_price * days) + additional_services
            tax = total_cost * tax_rate
            discount_amount = total_cost * discount
            total_bill = total_cost + tax - discount_amount
            return total_bill
    # Recursively check the next reservation
    return generate_bill(reservations[1:], rooms, room_number, days, additional_services, tax_rate, discount)

def room_occupancy_rate(rooms, occupied_count=0, total_rooms=0):
    """Recursively calculate room occupancy rate."""
    if not rooms:
        return occupied_count / total_rooms if total_rooms > 0 else 0.0  # base case
    room = rooms[0]
    if not room['available']:
        occupied_count += 1
    total_rooms += 1
    return room_occupancy_rate(rooms[1:], occupied_count, total_rooms)  # recursive call

def reservation_summary(reservations, unique_guests=None, total_reservations=0):
    """Recursively generate reservation summary."""
    if unique_guests is None:
        unique_guests = set()

    if not reservations:  # base case: no more reservations
        return {"totalReservations": total_reservations, "uniqueGuests": len(unique_guests)}

    reservation = reservations[0]
    unique_guests.add(reservation["customerName"])
    total_reservations += 1

    return reservation_summary(reservations[1:], unique_guests, total_reservations)  # recursive call

def view_customers(customers, customer_list=None):
    """Recursively list all customers."""
    if customer_list is None:
        customer_list = []

    if not customers:  # base case: no more customers
        return customer_list

    customer = customers[0]
    customer_list.append(customer)
    return view_customers(customers[1:], customer_list)  # recursive call

def view_all_rooms(rooms):
    """Recursively display all rooms."""
    if not rooms:  # base case: no more rooms
        return
    room = rooms[0]
    print(f"Room Number: {room['roomNumber']}, Type: {room['roomType']}, Price: ${room['price']}, Available: {'Yes' if room['available'] else 'No'}")
    return view_all_rooms(rooms[1:])  # recursive call
# --- REPORTS ---
def generate_occupancy_report(rooms: Tuple[Room, ...]) -> Dict[str, Any]:
    """Generate a report on room occupancy rates."""
    total_rooms = len(rooms)
    occupied_rooms = sum(1 for room in rooms if not room['available'])
    occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0
    return {"totalRooms": total_rooms, "occupiedRooms": occupied_rooms, "occupancyRate": occupancy_rate}

def generate_revenue_report(rooms: Tuple[Room, ...], reservations: Tuple[Reservation, ...], start_date: str, end_date: str) -> float:
    """Generate a revenue report for a specific period."""
    revenue = 0.0
    for reservation in reservations:
        res_start, res_end = reservation["dates"]
        if not (res_end < start_date or res_start > end_date):  # Check if reservation overlaps the period
            room = check_room_status(rooms, reservation["roomNumber"])
            if room:
                room_price = room['price']
                days = (datetime.strptime(res_end, "%Y-%m-%d") - datetime.strptime(res_start, "%Y-%m-%d")).days + 1
                revenue += room_price * days
    return revenue

def generate_financial_summary(rooms: Tuple[Room, ...], reservations: Tuple[Reservation, ...], start_date: str, end_date: str) -> Dict[str, Any]:
    """Generate financial summary including revenue and occupancy."""
    revenue = generate_revenue_report(rooms, reservations, start_date, end_date)
    occupancy_report = generate_occupancy_report(rooms)
    return {"totalRevenue": revenue, "occupancyRate": occupancy_report['occupancyRate']}

def validate_positive_integer(value: str) -> Optional[int]:
    """Validate if the input string is a positive integer."""
    try:
        value_int = int(value)
        if value_int >= 0:
            return value_int
        else:
            print("Value must be non-negative.")
            return None
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None

def validate_positive_float(value: str) -> Optional[float]:
    """Validate if the input string is a positive float."""
    try:
        value_float = float(value)
        if value_float >= 0:
            return value_float
        else:
            print("Value must be non-negative.")
            return None
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None

def display_menu():
    """Displays the main menu for the Hotel Management System."""
    print("\n--- Hotel Management System ---")
    print("1. Create Room")
    print("2. Check Room Status")
    print("3. Add Reservation")
    print("4. Add Customer")
    print("5. Release Room")
    print("6. Generate Bill")
    print("7. Check Room Occupancy Rate")
    print("8. View Reservation Summary")
    print("9. Search Customer")
    print("10. View Customers")
    print("11. View Room Details")
    print("12. View All Rooms")
    print("13. Generate Room Occupancy Report")
    print("14. Generate Revenue Report")
    print("15. Generate Financial Summary")
    print("16. Exit")


def main():
    """Main function to run the Hotel Management System."""
    # Load data from JSON files
    rooms = tuple(load_from_json("rooms.json"))
    customers = tuple(load_from_json("customers.json"))
    reservations = tuple(load_from_json("reservations.json"))

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == '1':  # Create Room
            try:
                room_number = int(input("Enter Room Number: "))
                if check_if_room_exists(rooms, room_number):
                    print(f"Room {room_number} already exists. Please enter a unique room number.")
                else:
                    room_type = input("Enter Room Type: ")
                    price = None
                    while price is None:
                        price_input = input("Enter Price: ")
                        price = validate_positive_integer(price_input)
                    available_input = input("Is the room available? (yes/no): ").strip().lower()
                    available = available_input == 'yes'

                    room = create_room(room_number, room_type, price, available)
                    rooms += (room,)
                    save_to_json("rooms.json", rooms)
                    print("Room created successfully!")

            except ValueError:
                print("Invalid input. Please enter valid details.")

        elif choice == '2':  # Check Room Status
            try:
                room_number = int(input("Enter Room Number to check status: "))
                room = check_room_status(rooms, room_number)
                if room:
                    print(f"Room Status: {'Available' if room['available'] else 'Not Available'}")
                else:
                    print("Room not found.")
            except ValueError:
                print("Invalid input. Please enter a valid room number.")

        elif choice == '3':  # Add Reservation
            try:
                customer_name = input("Enter Customer Name: ")
                room_number = int(input("Enter Room Number for Reservation: "))
                start_date = input("Enter Start Date (YYYY-MM-DD): ")
                end_date = input("Enter End Date (YYYY-MM-DD): ")
                reservation = create_reservation(customer_name, room_number, (start_date, end_date))
                result = add_reservation(reservations, rooms, reservation)
                if result:
                    reservations, rooms = result
                    save_to_json("reservations.json", reservations)
                    save_to_json("rooms.json", rooms)
                    print(f"Reservation added for {customer_name}.")
                else:
                    print(f"Failed to add reservation.")
            except ValueError:
                print("Invalid input. Please try again.")

        elif choice == '4':  # Add Customer
            try:
                name = input("Enter Customer Name: ")
                contact_info = input("Enter Contact Information: ")
                payment_method = input("Enter Payment Method: ")
                customers = add_customer(customers, name, contact_info, payment_method)
                save_to_json("customers.json", customers)
                print("Customer added successfully!")
            except ValueError:
                print("Invalid input. Please enter valid details.")
        elif choice == '5':  # Release Room
            try:
                room_number = int(input("Enter Room Number to Release: "))
                rooms = release_room(rooms, room_number)
                save_to_json("rooms.json", rooms)
                print(f"Room {room_number} is now available.")
            except ValueError:
                print("Invalid input. Please enter a valid room number.")

        elif choice == '6':  # Generate Bill
            try:
                room_number = int(input("Enter Room Number: "))
                days = int(input("Enter number of days stayed: "))
                additional_services = float(input("Enter additional services charges: "))
                tax_rate = float(input("Enter tax rate (in percentage): ")) / 100
                discount = float(input("Enter discount percentage: ")) / 100
                total_bill = generate_bill(reservations, rooms, room_number, days, additional_services, tax_rate, discount)
                if total_bill is not None:
                    print(f"Total Bill: ${total_bill:.2f}")
                else:
                    print("Reservation not found.")
            except ValueError:
                print("Invalid input. Please enter valid details.")

        elif choice == '7':  # Check Room Occupancy Rate
            occupancy_rate = room_occupancy_rate(rooms)
            print(f"Room Occupancy Rate: {occupancy_rate * 100:.2f}%")

        elif choice == '8':  # View Reservation Summary
            start_date = input("Enter Start Date (YYYY-MM-DD): ")
            end_date = input("Enter End Date (YYYY-MM-DD): ")
            filtered_reservations = filter_reservations_by_period(reservations, start_date, end_date)
            summary = reservation_summary(filtered_reservations)
            print(f"Total Reservations: {summary['totalReservations']}, Unique Guests: {summary['uniqueGuests']}")

        elif choice == '9':  # Search Customer
            name = input("Enter Customer Name: ")
            customer = search_customer(customers, name)
            if customer:
                print(f"Customer: {customer}")
            else:
                print("Customer not found.")

        elif choice == '10':  # View Customers
            customer_list = view_customers(customers)
            for customer in customer_list:
                print(customer)

        elif choice == '11':  # View Room Details
            room_number = int(input("Enter Room Number to view details: "))
            room = check_room_status(rooms, room_number)
            if room:
                print(f"Room Number: {room['roomNumber']}, Type: {room['roomType']}, Price: ${room['price']}, Available: {'Yes' if room['available'] else 'No'}")
            else:
                print("Room not found.")
        elif choice == '12':  # View All Rooms
            view_all_rooms(rooms)

        elif choice == '13':  # Generate Room Occupancy Report
            occupancy_report = generate_occupancy_report(rooms)
            print(f"Occupancy Report: {occupancy_report}")

        elif choice == '14':  # Generate Revenue Report
            start_date = input("Enter Start Date (YYYY-MM-DD): ")
            end_date = input("Enter End Date (YYYY-MM-DD): ")
            revenue = generate_revenue_report(rooms, reservations, start_date, end_date)
            print(f"Revenue for the period: ${revenue:.2f}")

        elif choice == '15':  # Generate Financial Summary
            start_date = input("Enter Start Date (YYYY-MM-DD): ")
            end_date = input("Enter End Date (YYYY-MM-DD): ")
            summary = generate_financial_summary(rooms, reservations, start_date, end_date)
            print(f"Financial Summary: {summary}")

        elif choice == '16':  # Exit
            print("Exiting system...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
