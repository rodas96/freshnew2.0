from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
from datetime import datetime
import re
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime


def get_total_pages(driver):
    try:
        page_counts_element = driver.find_element(
            By.CLASS_NAME, "search-results-module-page-counts"
        )
        page_counts_text = page_counts_element.text.strip()
        total_pages = int(page_counts_text.split()[-1].replace(",", ""))
        # 1 of x
        return total_pages
    except NoSuchElementException:
        logging.info("Only one page found.")
        return 1
    except Exception as e:
        logging.error(f"Error in get_total_pages: {str(e)}")
        raise e


# MISSING pass the sort_by if newest sort by applied doesnt make sense to keep going searching for the next page when the date already found isn't relevant
def extract_news_data(driver, search_phrase, months_to_consider):
    try:
        news_data = []
        promo_wrappers = driver.find_elements(By.CLASS_NAME, "promo-wrapper")

        for promo_wrapper in promo_wrappers:
            date = extract_date(promo_wrapper)
            if not date:
                logging.warning("No date found for news item.")

            if date not in months_to_consider:
                logging.info(f"Skipping news item from {date}")
                continue

            image_url = extract_image(promo_wrapper)
            if not image_url:
                logging.warning("No image found for news item.")
                continue

            promo_content = promo_wrapper.find_element(By.CLASS_NAME, "promo-content")

            title_element = promo_content.find_element(By.CLASS_NAME, "promo-title")
            title_text = title_element.text.strip()
            if not title_text:
                logging.warning("No title found for news item.")
                continue

            description = (
                extract_description(promo_content) or "No description available."
            )

            words_count = description.lower().count(search_phrase.lower())
            title_description = " ".join([title_text, description])
            match = re.search(r"\$|dollars|USD", title_description.lower())
            news_item = {
                "title": title_text,
                "description": description,
                "date": date,
                "image_url": image_url,
                "words_count": words_count,
                "has_dollar": match is not None,
            }
            news_data.append(news_item)

        logging.info("News data extracted successfully.")
        return news_data
    except Exception as e:
        logging.error(f"Error in extract_news_data: {str(e)}")
        raise e("Error in extract_news_data: " + str(e))


def extract_description(promo):
    try:
        description_element = promo.find_element(By.CLASS_NAME, "promo-description")
        description = description_element.text.strip() if description_element else ""
        logging.info(f"Extracted description from news: {description}")
        return description
    except Exception as e:
        logging.error(f"Failed to extract description from news: {str(e)}")


def extract_date(promo):
    try:
        timestamp_element = promo.find_element(By.CLASS_NAME, "promo-timestamp")
        if not timestamp_element:
            logging.error("Failed to extract timestamp from news")
            raise ValueError("Failed to extract timestamp from news")
        timestamp = timestamp_element.get_attribute("data-timestamp")
        formatted_date = format_timestamp(timestamp)
        logging.info(f"Extracted timestamp from news: {formatted_date}")
        return formatted_date
    except Exception as e:
        logging.error(f"Failed to extract date from news: {str(e)}")
        raise e("Failed to extract date from news: " + str(e))


def extract_image(promo):
    try:
        image_element = promo.find_element(By.CLASS_NAME, "image")
        image_url = image_element.get_attribute("src")
        response = requests.get(image_url)
        # Example:
        if response.status_code != 200:
            logging.warning(f"Failed to download image: {response.status_code}")
            return None

        if response.status_code == 200:
            filename = (
                f"{promo.text.split('\n')[1].split('.')[0][:10]}.jpg"
                if promo.text
                else f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            )
            directory = "output/pictures"
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(os.path.join(directory, filename), "wb") as file:
                file.write(response.content)

            logging.info(f"Image downloaded and saved as {filename} in {directory}")
            return os.path.join(directory, filename)
        else:
            logging.warning(f"Failed to download image: {response.status_code}")
            return None

    except Exception as e:
        logging.error(f"Error in extract_image: {str(e)}")
        return None


def format_timestamp(timestamp):
    try:
        timestamp_seconds = int(timestamp) / 1000
        dt_object = datetime.fromtimestamp(timestamp_seconds)
        formatted_date = dt_object.strftime("%m/%Y")
        return formatted_date
    except Exception as e:
        logging.error(f"Failed to format timestamp: {str(e)}")
