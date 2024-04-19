import logging
from initialization import initilization
from setup_search import setup_search
from scraper import extract_news_data, get_total_pages
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tenacity import retry, stop_after_attempt, wait_fixed
from time import sleep
from utils import generate_month_year_list, write_to_csv

cols_name = [
    "title",
    "description",
    "date",
    "image_url",
    "words_count",
    "has_dollar",
]
output_path = "output/news_data.csv"


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def navigate_to_page(driver, page_url):
    driver.get(page_url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "promo-content"))
    )


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def extract_data_with_retry(driver, search_phrase, months_to_consider):
    return extract_news_data(driver, search_phrase, months_to_consider)


def main():
    try:
        url = "https://www.latimes.com"
        driver, params = initilization()
        if not url:
            logging.warning("No URL provided.")
            raise ValueError("No URL provided.")
        current_url = setup_search(driver, url, params)
        sleep(10)  # Wait for correct number of pages to load after filtering
        pages_count = get_total_pages(driver)
        months_to_consider = generate_month_year_list(params["months_back"])
        news_data = []
        for number in range(1, pages_count + 1):
            page_url = f"{current_url}&p={number}"
            try:
                navigate_to_page(driver, page_url)
                extracted_data = extract_data_with_retry(
                    driver, params["search_phrase"], months_to_consider
                )
                news_data.extend(extracted_data)
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
