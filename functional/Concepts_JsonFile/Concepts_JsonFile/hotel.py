import json
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from functools import reduce

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
def filter_reservations_by_period(reservations: Tuple[Reservation], start_date: str, end_date: str) -> Tuple[Reservation]:
    """Using filter() for filtering reservations."""
    return tuple(
        filter(lambda res: start_date <= res["dates"][0] <= end_date, reservations)
    )

def room_occupancy_rate(rooms: Tuple[Room]) -> float:
    occupied_rooms = sum(1 for room in rooms if not room["available"])
    return occupied_rooms / len(rooms) if rooms else 0

def total_revenue(reservations: Tuple[Reservation], rooms: Tuple[Room]) -> float:
    """Use reduce to accumulate total revenue."""
    return reduce(
        lambda acc, reservation: acc + check_room_status(rooms, reservation["roomNumber"])["price"]
        if check_room_status(rooms, reservation["roomNumber"]) else acc,
        reservations, 0.0  # Start with 0.0 as the initial accumulator value
    )

def reservation_summary(reservations: Tuple[Reservation]) -> Dict[str, int]:
    """Use reduce to summarize reservations."""
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
    filtered_reservations = tuple(
        filter(lambda res: res["dates"][0].startswith(month), reservations)
    )
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
    print("13. Generate Daily Report")
    print("14. Generate Weekly Report")
    print("15. Generate Monthly Report")
    print("16. Exit")

def main():
    # Load data from JSON files
    rooms = tuple(load_from_json("room.json"))
    reservations = tuple(load_from_json("reservations.json"))
    customers = tuple(load_from_json("customers.json"))

    while True:
        display_menu()
        choice = input("Choose an option: ")

        if choice == '1':
            room_number = int(input("Enter room number: "))
            room_type = input("Enter room type: ")
            price = int(input("Enter room price: "))
            available = input("Is the room available? (yes/no): ").lower() == "yes"
            new_room = create_room(room_number, room_type, price, available)
            rooms += (new_room,)
            save_to_json("room.json", list(rooms))
        elif choice == '2':
            room_number = int(input("Enter room number: "))
            room = check_room_status(rooms, room_number)
            if room:
                print(room)
            else:
                print("Room not found.")
        elif choice == '3':
            customer_name = input("Enter customer name: ")
            room_number = int(input("Enter room number: "))
            dates = (input("Enter start date (YYYY-MM-DD): "), input("Enter end date (YYYY-MM-DD): "))
            reservation = create_reservation(customer_name, room_number, dates)
            result = add_reservation(reservations, rooms, reservation)
            if result:
                reservations, rooms = result
                save_to_json("reservations.json", list(reservations))
                save_to_json("room.json", list(rooms))
                print("Reservation added successfully.")
            else:
                print("Room is not available.")
        elif choice == '4':
            name = input("Enter customer name: ")
            contact_info = input("Enter contact information: ")
            payment_method = input("Enter payment method: ")
            customers = add_customer(customers, name, contact_info, payment_method)
            save_to_json("customers.json", list(customers))
            print(f"Customer {name} added successfully.")
        elif choice == '5':
            room_number = int(input("Enter room number: "))
            days = int(input("Enter number of days: "))
            additional_services = int(input("Enter additional services cost: "))
            bill = generate_bill(reservations, rooms, room_number, days, additional_services)
            if bill:
                print(f"Total bill: ${bill:.2f}")
            else:
                print("Reservation not found.")
        elif choice == '6':
            occupancy_rate = room_occupancy_rate(rooms)
            print(f"Occupancy Rate: {occupancy_rate * 100:.2f}%")
        elif choice == '7':
            summary = reservation_summary(reservations)
            print(f"Total Reservations: {summary['totalReservations']}")
            print(f"Unique Guests: {summary['uniqueGuests']}")
        elif choice == '8':
            room_number = int(input("Enter room number: "))
            rooms = release_room(rooms, room_number)
            save_to_json("room.json", list(rooms))
            print(f"Room {room_number} has been released.")
        elif choice == '9':
            name = input("Enter customer name: ")
            customer = search_customer(customers, name)
            if customer:
                print(customer)
            else:
                print("Customer not found.")
        elif choice == '10':
            print(view_customers(customers))
        elif choice == '11':
            room_number = int(input("Enter room number: "))
            room = check_room_status(rooms, room_number)
            if room:
                print(room)
            else:
                print("Room not found.")
        elif choice == '12':
            view_all_rooms(rooms)
        elif choice == '13':
            date = input("Enter date (YYYY-MM-DD): ")
            generate_daily_report(reservations, rooms, date)
        elif choice == '14':
            start_date = input("Enter start date (YYYY-MM-DD): ")
            generate_weekly_report(reservations, rooms, start_date)
        elif choice == '15':
            month = input("Enter month (YYYY-MM): ")
            generate_monthly_report(reservations, rooms, month)
        elif choice == '16':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
