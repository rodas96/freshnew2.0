import logging
from initialization import initilization
from setup_search import setup_search
from scrapper import extract_news_data
import json


def main():
    try:
        url = "https://www.latimes.com"
        driver, params = initilization()
        driver.maximize_window()
        if not url:
            logging.warning("No URL provided.")
            raise ValueError("No URL provided.")
        # Prepare search phrase topic, type and select sort by according to params specified
        setup_search(driver, url, params)
        news_data = extract_news_data(driver, params["search_phrase"])
        with open("news_data.json", "w") as f:
            json.dump(news_data, f, indent=4)
        driver.quit()
        print("Scraping completed successfully.")

        # Finalization steps
        logging.info("Scraping completed successfully.")

    except Exception as e:
        driver.quit()
        logging.error(f"Error in main: {str(e)}")
        raise e


if __name__ == "__main__":
    main()
