from datetime import datetime, timedelta
import csv
import logging


def get_month_year_back(months_back):
    current_date = datetime.now()
    target_date = current_date - timedelta(days=months_back * 30)
    return target_date.month, target_date.year


def generate_month_year_list(months_back):
    current_month, current_year = datetime.now().month, datetime.now().year
    month_year_list = []
    for i in range(months_back + 1):
        month = current_month - i
        year = current_year
        while month <= 0:
            month += 12
            year -= 1
        month_year_list.append(datetime(current_year, month, 1).strftime("%m/%Y"))
    return month_year_list


def write_to_csv(data, fieldnames, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        logging.info(f"Data written to {file_path} successfully.")
