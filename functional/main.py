from hotel import *
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
                room_number = input("Enter Room Number: ").strip()
                # Validate room number
                if not room_number.isdigit() or int(room_number) < 0:
                    print("Invalid input. Room number must be a positive integer.")
                    continue
                room_number = int(room_number)
                if check_if_room_exists(rooms, room_number):
                    print(f"Room {room_number} already exists. Please enter a unique room number.")
                else:
                    room_type = input("Enter Room Type: ")
                    price = None
                    while price is None:
                        price_input = input("Enter Price: ").strip()
                        # Validate price
                        if not price_input.replace('.', '', 1).isdigit() or float(price_input) < 0:
                            print("Invalid input. Price must be a positive number.")
                        else:
                            price = float(price_input)
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
                room_number = input("Enter Room Number to check status: ").strip()
                if not room_number.isdigit() or int(room_number) < 0:
                    print("Invalid input. Room number must be a positive integer.")
                    continue
                room_number = int(room_number)
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
                room_number = input("Enter Room Number for Reservation: ").strip()
                if not room_number.isdigit() or int(room_number) < 0:
                    print("Invalid input. Room number must be a positive integer.")
                    continue
                room_number = int(room_number)

                start_date = input("Enter Start Date (YYYY-MM-DD): ")
                end_date = input("Enter End Date (YYYY-MM-DD): ")
                reservation = create_reservation(customer_name, room_number, (start_date, end_date))
                result = add_reservation_if_customer_exists(reservations, rooms, customers, reservation)
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
                room_number = input("Enter Room Number to Release: ").strip()
                if not room_number.isdigit() or int(room_number) < 0:
                    print("Invalid input. Room number must be a positive integer.")
                    continue
                room_number = int(room_number)
                rooms = release_room(rooms, room_number)
                save_to_json("rooms.json", rooms)
                print(f"Room {room_number} is now available.")
            except ValueError:
                print("Invalid input. Please enter a valid room number.")

        elif choice == '6':  # Generate Bill
            try:
                room_number = input("Enter Room Number: ").strip()
                if not room_number.isdigit() or int(room_number) < 0:
                    print("Invalid input. Room number must be a positive integer.")
                    continue
                room_number = int(room_number)

                days = input("Enter number of days stayed: ").strip()
                if not days.isdigit() or int(days) < 0:
                    print("Invalid input. Days must be a positive integer.")
                    continue
                days = int(days)

                additional_services = input("Enter additional services charges: ").strip()
                if not additional_services.replace('.', '', 1).isdigit() or float(additional_services) < 0:
                    print("Invalid input. Additional services charges must be a positive number.")
                    continue
                additional_services = float(additional_services)

                tax_rate = input("Enter tax rate (in percentage): ").strip()
                if not tax_rate.replace('.', '', 1).isdigit() or float(tax_rate) < 0:
                    print("Invalid input. Tax rate must be a positive number.")
                    continue
                tax_rate = float(tax_rate) / 100

                discount = input("Enter discount percentage: ").strip()
                if not discount.replace('.', '', 1).isdigit() or float(discount) < 0:
                    print("Invalid input. Discount must be a positive number.")
                    continue
                discount = float(discount) / 100

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
