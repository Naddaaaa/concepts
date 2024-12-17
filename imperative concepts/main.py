from database import Database
from datetime import datetime
from room import Room
from reservation import Reservation
from customer import CustomerManager
from Billing import Billing
from reporting import Reporting
from datetime import datetime


def main():
    # Initialize database
    db = Database()
    db.connect()
    db.create_tables()  # Ensure all tables are created

    # Initialize managers
    room_manager = Room(db)
    reservation_manager = Reservation(db, room_manager)
    customer_manager = CustomerManager(db)
    billing_manager = Billing(db)
    reporting = Reporting(db)
    '''
    db.execute_query("""
    INSERT INTO reservations (customerID, roomNumber, checkInDate, checkOutDate)
    VALUES 
        (1, 101, '2024-05-16', '2024-05-20'),
        (2, 102, '2024-05-17', '2024-05-19'),
        (3, 101, '2024-05-18', '2024-05-22')
    """)
    print("Test data inserted for reservations.")
    '''
    # Interactive menu
    while True:
        print("\nHotel Management System")
        print("1. Add Room")
        print("2. Check Room Availability")
        print("3. Book Room")
        print("4. Release Room")
        print("5. Show All Rooms")
        print("6. Make Reservation")
        print("7. Add Customer")
        print("8. Search Customer")
        print("9. Update Customer")
        print("10. Generate Bill")
        print("11. Generate Report")
        print("12. Exit")
        

        choice = input("Enter your choice: ")
        
        if choice == "1":
            room_number = int(input("Enter room number: "))
            room_type = input("Enter room type (single/double/suite): ")
            price = float(input("Enter price: "))
            room_manager.add_room(room_number, room_type, price)
        elif choice == "2":
            room_number = int(input("Enter room number: "))
            check_in_time = input("Enter check-in time (YYYY-MM-DD): ")
            check_out_time = input("Enter check-out time (YYYY-MM-DD): ")
            available = room_manager.check_availability(room_number, check_in_time, check_out_time)
            status = "Available" if available else "Not Available"
            print(f"Room {room_number} is {status}.")
        elif choice == "3":
            room_number = int(input("Enter room number: "))
            customer_name = input("Enter customer name: ")
            check_in_time = input("Enter check-in time (YYYY-MM-DD HH:MM:SS): ")
            check_out_time = input("Enter check-out time (YYYY-MM-DD HH:MM:SS): ")
            room_manager.book_room(room_number, customer_name, check_in_time, check_out_time)
        elif choice == "4":
            room_number = int(input("Enter room number: "))
            room_manager.release_room(room_number)
        elif choice == "5":
            room_manager.show_rooms()
        elif choice == "6":
            customer_name = input("Enter customer name: ")
            room_number = int(input("Enter room number: "))
            check_in_date = input("Enter check-in date (YYYY-MM-DD): ")
            check_out_date = input("Enter check-out date (YYYY-MM-DD): ")
            reservation_manager.make_reservation(customer_name, room_number, check_in_time, check_out_time)
        elif choice == "7":
            name = input("Enter customer name: ")
            contact_info = input("Enter customer contact info: ")
            payment_method = input("Enter payment method: ")
            customer_manager.add_customer(name, contact_info, payment_method)
        elif choice == "8":
            name = input("Enter customer name to search: ")
            customer_manager.search_customer(name)
        elif choice == "9":
            customer_name = input("Enter customer name to update: ")
            name = input("Enter new name (leave blank to keep current): ")
            contact_info = input("Enter new contact info (leave blank to keep current): ")
            payment_method = input("Enter new payment method (leave blank to keep current): ")
            customer_manager.update_customer(customer_name, name or None, contact_info or None, payment_method or None)
        elif choice == '10':
            room_number = int(input("Enter room number for the bill: "))
            
            # Get the room details (room type, customer_id)
            room = room_manager.get_room_details(room_number)
            if room:
                customer_id = room["customer_id"]
                if customer_id:
                    # Proceed with generating the bill
                    check_in_date = input("Enter check-in date (YYYY-MM-DD): ")
                    check_out_date = input("Enter check-out date (YYYY-MM-DD): ")
                    
                    # Convert strings to date objects and calculate duration
                    check_in_date = datetime.strptime(check_in_date, "%Y-%m-%d")
                    check_out_date = datetime.strptime(check_out_date, "%Y-%m-%d")
                    duration = (check_out_date - check_in_date).days
                    
                    services = input("Enter additional services (e.g., meals, laundry): ").split(",")  # Split services into a list
                    discount_percentage = float(input("Enter discount percentage (if any, 0 if none): "))  # Optional discount

                    bill = billing_manager.generate_bill(customer_id, room_number, room["room_type"], duration, services, discount_percentage)
                    print(f"Bill for room {room_number}:")
                    print(bill)
                else:
                    print("No customer is linked to this room.")
            else:
                print("Room not found.")
        elif choice == "11":
             print("1. Room Occupancy Report")
             
             report_choice = input("Enter report choice: ")
             start_date = input("Enter start date (YYYY-MM-DD): ")
             end_date = input("Enter end date (YYYY-MM-DD): ")

             if report_choice == "1":
                reporting.room_occupancy_rate(start_date, end_date)
             else:
               print("Invalid report choice.")
        elif choice == "12":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

    # Close database connection
    db.close()

if __name__ == "__main__":
    main()
