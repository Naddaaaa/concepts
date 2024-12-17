from datetime import datetime, timedelta

class Reporting:
    def __init__(self, db):
        self.db = db

    def room_occupancy_rate(self, start_date, end_date):
       query = """
       SELECT roomNumber, COUNT(*) as occupancy
       FROM reservations
       WHERE (checkInDate BETWEEN ? AND ?) OR (checkOutDate BETWEEN ? AND ?)
       GROUP BY roomNumber
       """
       data = self.db.fetch_all(query, (start_date, end_date, start_date, end_date))
       print("Room Occupancy Report:")
       if data:
           for row in data:
               print(f"Room {row[0]} was occupied {row[1]} times.")  # Use numeric indices
       else:
            print("No occupancy data available for the given dates.")
