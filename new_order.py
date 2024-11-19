# E:\WorkSpace\js\order\new_order.py
# New entry point for booking.
from book import Booking

if __name__ == '__main__':
    # User-provided booking parameters
    date = "2024-11-02"
    serviceid = "42"
    venue_index = 0
    users = "160734"
    username = "22011207"
    password = "040019"

    book = Booking(date=date, serviceid=serviceid, venue_index=venue_index, users=users, username=username, password=password)
    book.pre_book()