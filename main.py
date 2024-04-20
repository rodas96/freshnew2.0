import logging
from initialization import initilization
from setup_search import setup_search
from scraper import extract_news_data, get_total_pages, navigate_to_page
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tenacity import retry, stop_after_attempt, wait_fixed
from time import sleep
from utils import relevant_months, write_to_csv

cols_name = [
    "title",
    "description",
    "date",
    "image_url",
    "words_count",
    "has_dollar",
]
output_path = "output/news_data.csv"
news_data = []


def main():
    try:
        url = "https://www.latimes.com"
        driver, params = initilization()
        if not url:
            logging.warning("No URL provided.")
            raise ValueError("No URL provided.")
        current_url = setup_search(driver, url, params)
        sleep(
            6
        )  # Wait for correct number of pages to load after filtering its visible anyway but the data is not loadedto count the pages
        pages_count = get_total_pages(driver)
        max_pages = min(
            pages_count, 25
        )  # define here if want to check the time of extraction for a large quantity like 1k 5k 10k images and news.
        logging.info(f"Total pages to extract: {pages_count}")
        months_to_consider = relevant_months(params["months_back"])
        logging.info(f"Months to consider extracting the news: {months_to_consider}")
        for number in range(1, max_pages + 1):
            page_url = f"{current_url}&p={number}"
            try:
                navigate_to_page(driver, page_url)
                extracted_data, date_over = extract_news_data(
                    driver,
                    params["search_phrase"],
                    months_to_consider,
                    params["sort_by"],
                )
                news_data.extend(extracted_data)
                if date_over:
                    logging.info("Date over. Stopping the extraction.")
                    break
            except Exception as e:
                logging.error(f"Error extracting data from page {number}: {str(e)}")
                continue

        write_to_csv(news_data, cols_name, output_path)
        driver.quit()
        logging.info("Data extracted successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        driver.quit()
        raise e


if __name__ == "__main__":
    main()
