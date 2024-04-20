from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from tenacity import retry, stop_after_attempt, wait_fixed
from selenium.common.exceptions import NoSuchElementException


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def setup_search(driver, url, params):
    try:
        search(driver, url, params)
        select_topic_type(driver, params)
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


@retry(stop=stop_after_attempt(5), wait=wait_fixed(4))
def select_topic_type(driver, params):
    try:
        if not params["news_topic"]:
            raise ValueError("No news topic specified.")
        if not params["news_type"]:
            raise ValueError("No news type specified.")

        topic_name = params.get("news_topic")
        type_name = params.get("news_type")

        check_topic = driver.find_element(
            By.XPATH,
            f"//label[contains(@class, 'checkbox-input-label')]/span[text()='{topic_name}']/preceding-sibling::input[@type='checkbox']",
        )
        check_topic.click()
        check_type = driver.find_element(
            By.XPATH,
            f"//label[contains(@class, 'checkbox-input-label') and .//span[text()='{type_name}']]/input[@type='checkbox']",
        )
        check_type.click()

    except NoSuchElementException as e:
        logging.error(f"Element not found: {str(e)}")
        raise e
    except ValueError as e:
        logging.error(str(e))
        raise e
    except Exception as e:
        logging.error(f"Error in select_topic_type: {str(e)}")
        raise RuntimeError("Error in select_topic_type: " + str(e))


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
