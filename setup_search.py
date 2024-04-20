from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from tenacity import retry, stop_after_attempt, wait_fixed


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def setup_search(driver, url, params):
    try:
        search(driver, url, params)
        select_topic(driver, params)
        sort_by(driver, params)
        logging.info("Search setup completed successfully.")
        driver.refresh()
        return driver.current_url
    except Exception as e:
        logging.error(f"Error in setup_search: {str(e)}")
        raise e("Error in setup_search: " + str(e))


def search(driver, url, params):
    try:
        search_url = f"{url}/search?q={params['search_phrase']}"
        driver.get(search_url)
        no_result = driver.find_elements(
            By.CLASS_NAME, "search-results-module-no-results"
        )
        if no_result:
            logging.error("No results found for the search phrase")
            raise ValueError("No results found for the search phrase")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "search-results-module-input")
            )
            and EC.text_to_be_present_in_element_value(
                (By.CLASS_NAME, "search-results-module-input"), params["search_phrase"]
            )
        )
        logging.info(f"Search phrase '{params['search_phrase']}' entered successfully.")
        return driver
    except Exception as e:
        logging.error(f"Error in search_topic: {str(e)}")
        raise e


def select_topic(driver, params):
    try:
        if not params["news_topic"]:
            raise ValueError("No news topic specified.")

        topic_name = params.get("news_topic")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//label[contains(@class, 'checkbox-input-label') and span[text()='{topic_name}']]/input[@type='checkbox']",
                )
            )
        )
        check_topic = driver.find_element(
            By.XPATH,
            f"//label[contains(@class, 'checkbox-input-label') and span[text()='{topic_name}']]/input[@type='checkbox']",
        )
        check_topic.click()
    except Exception as e:
        logging.error(f"Error in select_topic: {str(e)}")
        raise e("Error in select_topic: " + str(e))


def sort_by(driver, params):
    try:
        if not params["sort_by"]:
            logging.warning("No sort by option specified.")
            return

        sort_by_value = params["sort_by"]
        select = Select(driver.find_element(By.CLASS_NAME, "select-input"))
        select.select_by_visible_text(sort_by_value)
        logging.info(f"Sorted by '{sort_by_value}'")

    except Exception as e:
        logging.warning(f"Not possible to sort_by: {str(e)}")
