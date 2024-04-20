from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv
import logging


def relevant_months(months_back):
    current_date = datetime.now()
    target_date = current_date
    target_date -= relativedelta(months=months_back - 1)

    month_year_list = []
    while target_date <= current_date:
        month_year_list.append(target_date.strftime("%m/%Y"))
        target_date += relativedelta(months=1)

    return month_year_list


def write_to_csv(data, fieldnames, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        logging.info(f"Data written to {file_path} successfully.")
