import json
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from functools import reduce as builtin_reduce  # Using Python's built-in reduce for comparison

# Data Types
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
    return {"roomNumber": room_number, "roomType": room_type, "price": price, "available": available}

def update_room_availability(rooms: Tuple[Room], room_number: int, availability: bool) -> Tuple[Room]:
    """Recursively update room availability."""
    if not rooms:
        return ()
    room = rooms[0]
    if room["roomNumber"] == room_number:
        updated_room = {**room, 'available': availability}
        return (updated_room,) + update_room_availability(rooms[1:], room_number, availability)
    return (room,) + update_room_availability(rooms[1:], room_number, availability)

def check_room_status(rooms: Tuple[Room], room_number: int) -> Optional[Room]:
    """Recursively find room by number."""
    if not rooms:
        return None
    room = rooms[0]
    if room["roomNumber"] == room_number:
        return room
    return check_room_status(rooms[1:], room_number)

def release_room(rooms: Tuple[Room], room_number: int) -> Tuple[Room]:
    updated_rooms = update_room_availability(rooms, room_number, True)
    return updated_rooms

def view_all_rooms(rooms: Tuple[Room]) -> None:
    """Display details of all rooms."""
    if not rooms:
        print("No rooms available.")
        return
    for room in rooms:
        print(f"Room Number: {room['roomNumber']}")
        print(f"Room Type: {room['roomType']}")
        print(f"Price: ${room['price']}")
        print(f"Available: {'Yes' if room['available'] else 'No'}")
        print("-" * 30)

# --- RESERVATION SYSTEM ---
def create_reservation(customer_name: str, room_number: int, dates: Tuple[str, str]) -> Reservation:
    return {"customerName": customer_name, "roomNumber": room_number, "dates": dates}

def add_reservation(
    reservations: Tuple[Reservation],
    rooms: Tuple[Room],
    reservation: Reservation
) -> Optional[Tuple[Tuple[Reservation], Tuple[Room]]]:
    room = check_room_status(rooms, reservation["roomNumber"])
    if room and room["available"]:
        updated_rooms = update_room_availability(rooms, reservation["roomNumber"], False)
        updated_reservations = reservations + (reservation,)
        return (updated_reservations, updated_rooms)
    return None

# --- CUSTOMER MANAGEMENT ---
def add_customer(customers: Tuple[Customer], name: str, contact_info: str, payment_method: str) -> Tuple[Customer]:
    customer = {"name": name, "contactInfo": contact_info, "paymentMethod": payment_method}
    updated_customers = (customer,) + customers
    return updated_customers

def search_customer(customers: Tuple[Customer], name: str) -> Optional[Customer]:
    """Recursively search for customer by name."""
    if not customers:
        return None
    customer = customers[0]
    if customer["name"] == name:
        return customer
    return search_customer(customers[1:], name)

def view_customers(customers: Tuple[Customer]) -> Tuple[str]:
    return tuple(customer["name"] for customer in customers)

# --- BILLING SYSTEM ---
def calculate_bill(
    room_price: int,
    days: int,
    additional_services: int = 0,
    tax_rate: float = 0.1,
    discount: float = 0.0
) -> float:
    subtotal = room_price * days + additional_services
    tax = subtotal * tax_rate
    return subtotal + tax - discount

def generate_bill(
    reservations: Tuple[Reservation],
    rooms: Tuple[Room],
    room_number: int,
    days: int,
    additional_services: int = 0
) -> Optional[float]:
    reservation = next((res for res in reservations if res["roomNumber"] == room_number), None)
    if reservation:
        room = check_room_status(rooms, room_number)
        if room:
            return calculate_bill(room["price"], days, additional_services)
    return None

# --- REPORTING AND ANALYTICS ---
def custom_filter(func, items):
    """Custom filter implementation using recursion."""
    if not items:  # Base case: if the list is empty, return an empty list
        return []
    if func(items[0]):  # If the condition is met for the first item
        return [items[0]] + custom_filter(func, items[1:])  # Include the item and recursively filter the rest
    return custom_filter(func, items[1:])  # Otherwise, just skip the item and continue filtering

def reduce(func, items, initial_value):
    """Custom reduce implementation using recursion."""
    if not items:
        return initial_value
    return reduce(func, items[1:], func(initial_value, items[0]))

def filter_reservations_by_period(reservations: Tuple[Reservation], start_date: str, end_date: str) -> Tuple[Reservation]:
    """Custom filter function for filtering reservations by period."""
    def condition(reservation):
        return start_date <= reservation["dates"][0] <= end_date
    
    return tuple(custom_filter(condition, reservations))  # Use custom filter

def room_occupancy_rate(rooms: Tuple[Room]) -> float:
    occupied_rooms = sum(1 for room in rooms if not room["available"])
    return occupied_rooms / len(rooms) if rooms else 0

def total_revenue(reservations: Tuple[Reservation], rooms: Tuple[Room]) -> float:
    """Use custom reduce to accumulate total revenue."""
    return reduce(
        lambda acc, reservation: acc + check_room_status(rooms, reservation["roomNumber"])["price"]
        if check_room_status(rooms, reservation["roomNumber"]) else acc,
        reservations, 0.0  # Start with 0.0 as the initial accumulator value
    )

def reservation_summary(reservations: Tuple[Reservation]) -> Dict[str, int]:
    """Use custom reduce to summarize reservations."""
    total_reservations = len(reservations)
    unique_guests = len(
        reduce(lambda acc, res: acc | {res["customerName"]}, reservations, set())
    )  # Using a set to count unique customer names
    return {
        "totalReservations": total_reservations,
        "uniqueGuests": unique_guests
    }

# --- GENERATING PERIODIC REPORTS ---
def generate_daily_report(reservations: Tuple[Reservation], rooms: Tuple[Room], date: str):
    filtered_reservations = filter_reservations_by_period(reservations, date, date)
    revenue = total_revenue(filtered_reservations, rooms)
    occupancy_rate = room_occupancy_rate(rooms)
    print(f"--- Daily Report for {date} ---")
    print(f"Revenue: ${revenue:.2f}")
    print(f"Occupancy Rate: {occupancy_rate * 100:.2f}%")
    print(f"Total Reservations: {len(filtered_reservations)}")

def generate_weekly_report(reservations: Tuple[Reservation], rooms: Tuple[Room], start_date: str):
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = start_date_obj + timedelta(weeks=1)
    end_date = end_date_obj.strftime("%Y-%m-%d")

    filtered_reservations = filter_reservations_by_period(reservations, start_date, end_date)
    revenue = total_revenue(filtered_reservations, rooms)
    occupancy_rate = room_occupancy_rate(rooms)
    print(f"--- Weekly Report from {start_date} to {end_date} ---")
    print(f"Revenue: ${revenue:.2f}")
    print(f"Occupancy Rate: {occupancy_rate * 100:.2f}%")
    print(f"Total Reservations: {len(filtered_reservations)}")

def generate_monthly_report(reservations: Tuple[Reservation], rooms: Tuple[Room], month: str):
    def condition(reservation):
        return reservation["dates"][0].startswith(month)
    
    filtered_reservations = tuple(custom_filter(condition, reservations))  # Use custom filter
    revenue = total_revenue(filtered_reservations, rooms)
    occupancy_rate = room_occupancy_rate(rooms)
    print(f"--- Monthly Report for {month} ---")
    print(f"Revenue: ${revenue:.2f}")
    print(f"Occupancy Rate: {occupancy_rate * 100:.2f}%")
    print(f"Total Reservations: {len(filtered_reservations)}")

# --- MAIN FUNCTION ---
def display_menu():
    print("\n--- Hotel Management System ---")
    print("1. Create Room")
    print("2. Check Room Status")
    print("3. Add Reservation")
    print("4. Add Customer")
    print("5. Generate Bill")
    print("6. Check Room Occupancy Rate")
    print("7. View Reservation Summary")
    print("8. Release Room")
    print("9. Search Customer")
    print("10. View Customers")
    print("11. View Room Details")
    print("12. View All Rooms")
    print("13. Daily Report")
    print("14. Weekly Report")
    print("15. Monthly Report")
    print("16. Exit")

def main():
    # Placeholder for room, customer, and reservation data
    rooms = tuple()
    customers = tuple()
    reservations = tuple()

    while True:
        display_menu()
        choice = int(input("Enter your choice: "))

        if choice == 1:
            room_number = int(input("Enter Room Number: "))
            room_type = input("Enter Room Type: ")
            price = int(input("Enter Price: "))
            available = input("Is the room available? (yes/no): ").lower() == 'yes'
            room = create_room(room_number, room_type, price, available)
            rooms += (room,)
            print("Room Created Successfully!")

        elif choice == 2:
            room_number = int(input("Enter Room Number to check status: "))
            room = check_room_status(rooms, room_number)
            if room:
                print(f"Room Status: {'Available' if room['available'] else 'Not Available'}")
            else:
                print("Room not found.")

        elif choice == 3:
            customer_name = input("Enter Customer Name: ")
            room_number = int(input("Enter Room Number for reservation: "))
            start_date = input("Enter Start Date (YYYY-MM-DD): ")
            end_date = input("Enter End Date (YYYY-MM-DD): ")
            reservation = create_reservation(customer_name, room_number, (start_date, end_date))
            result = add_reservation(reservations, rooms, reservation)
            if result:
                reservations, rooms = result
                print("Reservation Added Successfully!")
            else:
                print("Room is unavailable for the selected dates.")

        elif choice == 4:
            name = input("Enter Customer Name: ")
            contact_info = input("Enter Contact Information: ")
            payment_method = input("Enter Payment Method: ")
            customers = add_customer(customers, name, contact_info, payment_method)
            print("Customer Added Successfully!")

        elif choice == 5:
            room_number = int(input("Enter Room Number for the bill: "))
            days = int(input("Enter Number of Days: "))
            additional_services = int(input("Enter Additional Services Costs: "))
            bill = generate_bill(reservations, rooms, room_number, days, additional_services)
            if bill is not None:
                print(f"Total Bill: ${bill:.2f}")
            else:
                print("Reservation not found.")

        elif choice == 6:
            occupancy_rate = room_occupancy_rate(rooms)
            print(f"Occupancy Rate: {occupancy_rate * 100:.2f}%")

        elif choice == 7:
            summary = reservation_summary(reservations)
            print(f"Total Reservations: {summary['totalReservations']}")
            print(f"Unique Guests: {summary['uniqueGuests']}")

        elif choice == 8:
            room_number = int(input("Enter Room Number to release: "))
            rooms = release_room(rooms, room_number)
            print("Room Released Successfully!")

        elif choice == 9:
            customer_name = input("Enter Customer Name to search: ")
            customer = search_customer(customers, customer_name)
            if customer:
                print(f"Customer Found: {customer}")
            else:
                print("Customer not found.")

        elif choice == 10:
            customers_list = view_customers(customers)
            print("Customers:")
            for customer_name in customers_list:
                print(customer_name)

        elif choice == 11:
            room_number = int(input("Enter Room Number to view details: "))
            room = check_room_status(rooms, room_number)
            if room:
                print(f"Room Details: {room}")
            else:
                print("Room not found.")

        elif choice == 12:
            view_all_rooms(rooms)

        elif choice == 13:
            date = input("Enter date for the daily report (YYYY-MM-DD): ")
            generate_daily_report(reservations, rooms, date)

        elif choice == 14:
            start_date = input("Enter start date for the weekly report (YYYY-MM-DD): ")
            generate_weekly_report(reservations, rooms, start_date)

        elif choice == 15:
            month = input("Enter month for the monthly report (YYYY-MM): ")
            generate_monthly_report(reservations, rooms, month)

        elif choice == 16:
            print("Exiting the system.")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
