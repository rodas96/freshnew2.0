from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import os
import requests
from datetime import datetime
import re


def extract_news_data(driver, search_phrase):
    try:
        driver.refresh()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "promo-content"))
        )
        news_data = []
        titles = driver.find_elements(By.CLASS_NAME, "promo-content")

        for title in titles:
            title_element = title.find_element(By.CLASS_NAME, "promo-title")
            title_text = title_element.text.strip()
            if not title_text:
                raise ValueError("Failed to extract title from news")

            description = extract_description(title)
            date = extract_date(title)
            image_url = extract_image(driver, title_text)

            if not image_url:
                logging.warning(f"Failed to extract image for {title_text}")
                image_url = "No image available"

            words_count = description.lower().count(search_phrase.lower())
            title_description = str.join(" ", [title_text, description])
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
        return news_data


def extract_description(title):
    try:
        description_element = title.find_element(By.CLASS_NAME, "promo-description")
        description = description_element.text.strip() if description_element else ""
        logging.info(f"Extracted description from news: {description}")
        return description
    except Exception as e:
        logging.error(f"Failed to extract description from news: {str(e)}")
        raise e("Failed to extract description from news: " + str(e))


def extract_date(title):
    try:
        timestamp_element = title.find_element(By.CLASS_NAME, "promo-timestamp")
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


def extract_image(driver, title):
    try:
        image = driver.find_element(By.CLASS_NAME, "image")
        image_url = image.get_attribute("src")
        response = requests.get(image_url)

        if response.status_code == 200:
            filename = f"{title.replace(' ', '_')}.jpg"
            directory = "pictures"
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
    timestamp_seconds = int(timestamp) / 1000
    dt_object = datetime.fromtimestamp(timestamp_seconds)
    formatted_date = dt_object.strftime("%m/%d/%Y")
    return formatted_date
