# E:\WorkSpace\js\order\fetch_service_data.py
# Entry point for fetching service data.
from fetch_data import FetchData

def fetch_service_entry(date, serviceid):
    data = FetchData.fetch_service_data(date, serviceid)
    if data:
        FetchData.save_data_to_json(data, date, serviceid)
        print("Data fetched and saved successfully.")
    else:
        print("Failed to fetch data.")

if __name__ == '__main__':
    date = input("Enter the date (YYYY-MM-DD): ")
    serviceid = input("Enter the service ID: ")
    fetch_service_entry(date, serviceid)
    FetchData.visualize_booking_data(date, serviceid)
