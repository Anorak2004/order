from order.book import Booking

if __name__ == '__main__':
    book = Booking(stockid="10564",serviceid="22", users="22011202", username="22011201", password="160571")
    book.pre_book()