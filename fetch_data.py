# E:\WorkSpace\js\order\fetch_data.py
# Module to fetch venue data based on date and service ID.
import requests
import json
import os
import pandas as pd
from config import Config

class FetchData:
    @staticmethod
    def fetch_service_data(date, serviceid):
        url = f"{Config.BASE_URL}/cgyd/product/findOkArea.html"
        params = {
            "s_date": date,
            "serviceid": serviceid
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get('object')
            return data if data else None
        else:
            print(f"Request failed, status code: {response.status_code}")
            return None

    @staticmethod
    def save_data_to_json(data, date, serviceid):
        folder = 'data'
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, f"service_data_{serviceid}_{date}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")

    @staticmethod
    def load_data_from_json(date, serviceid):
        folder = 'data'
        filename = os.path.join(folder, f"service_data_{serviceid}_{date}.json")
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return None

    @staticmethod
    def get_booking_params(data, venue_index=0):
        """
        Extracts booking parameters from the provided data.
        :param data: The data loaded from JSON or fetched from the API.
        :param venue_index: Index of the venue to select for booking.
        :return: Dictionary with booking parameters.
        """
        if not data or len(data) <= venue_index:
            raise ValueError("Invalid data or venue index")
        venue = data[venue_index]
        booking_params = {
            'id': venue['id'],
            'stockid': venue['stockid'],
            'serviceid': venue['stock']['serviceid'],
            'sname': venue['sname'],
            's_date': venue['stock']['s_date'],
            'time_no': venue['stock']['time_no']
        }
        return booking_params

    @staticmethod
    def prepare_booking_params(date, serviceid, venue_index=0):
        """
        Load data from JSON or fetch data if not available and prepare booking parameters.
        :param date: Date for the booking.
        :param serviceid: Service ID for the booking.
        :param venue_index: Index of the venue to select for booking.
        :return: Dictionary with booking parameters.
        """
        data = FetchData.load_data_from_json(date, serviceid)
        if not data:
            data = FetchData.fetch_service_data(date, serviceid)
            if data:
                FetchData.save_data_to_json(data, date, serviceid)
            else:
                raise Exception("Failed to fetch venue data")
        return FetchData.get_booking_params(data, venue_index)

    @staticmethod
    def visualize_booking_data(date, serviceid):
        """
        Visualize booking data for better understanding and selection.
        :param date: Date for the booking.
        :param serviceid: Service ID for the booking.
        """
        data = FetchData.load_data_from_json(date, serviceid)
        if not data:
            data = FetchData.fetch_service_data(date, serviceid)
            if data:
                FetchData.save_data_to_json(data, date, serviceid)
            else:
                raise Exception("Failed to fetch venue data")

        # Create a dictionary to store venue information by name and time slot
        venue_dict = {}
        for index, venue in enumerate(data):
            sname = venue['sname']
            time_no = venue['stock']['time_no']
            if sname not in venue_dict:
                venue_dict[sname] = {}
            venue_dict[sname][time_no] = {
                'Venue ID': venue['id'],
                'Stock ID': venue['stockid'],
                'Service ID': venue['stock']['serviceid'],
                'Date': venue['stock']['s_date'],
                'Index': index
            }

        # Generate a visual representation using text
        time_slots = sorted({time_no for venue in venue_dict.values() for time_no in venue})
        header = "| Venue Name        | " + " | ".join(time_slots) + " |"
        separator = "|-------------------|" + "|-------------------" * len(time_slots) + "|"
        rows = []

        for sname, times in venue_dict.items():
            row = f"| {sname:<17} | "
            row_data = []
            for time_no in time_slots:
                if time_no in times:
                    row_data.append(f"Index: {times[time_no]['Index']}, ID: {times[time_no]['Venue ID']}, Stock: {times[time_no]['Stock ID']}")
                else:
                    row_data.append("N/A")
            row += " | ".join(row_data) + " |"
            rows.append(row)

        # Print the table
        print(header)
        print(separator)
        for row in rows:
            print(row)
