from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Setup search phrase, topic, type and sort by options according to params specified


def setup_search(driver, url, params):
    try:
        search(driver, url, params)
        select_topic_type(driver, params)
        sort_by(driver, params)
        logging.info("Search setup completed successfully.")
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


def select_topic_type(driver, params):
    try:
        if not params["news_topic"]:
            logging.warning("No news topic specified.")
        if not params["news_type"]:
            logging.warning("No news type specified.")

        topic_name = params.get("news_topic")
        type_name = params.get("news_type")
        topic_selected = False
        type_selected = False
        checkboxes = driver.find_elements(
            By.CSS_SELECTOR, "label.checkbox-input-label > span"
        )

        for checkbox in checkboxes:
            if topic_name and not topic_selected and checkbox.text == topic_name:
                checkbox_input = checkbox.find_element(
                    By.XPATH, "./preceding-sibling::input[@type='checkbox']"
                )
                if checkbox_input.is_displayed() and not checkbox_input.is_selected():
                    checkbox_input.click()
                    logging.info(f"Topic checkbox '{topic_name}' selected.")
                    topic_selected = True
                    WebDriverWait(driver, 20).until(
                        EC.visibility_of_all_elements_located(
                            (By.CLASS_NAME, "search-filter-menu-wrapper")
                        )
                    )

            if type_name and not type_selected and checkbox.text == type_name:
                checkbox_input = checkbox.find_element(
                    By.XPATH, "./preceding-sibling::input[@type='checkbox']"
                )
                if checkbox_input.is_displayed() and not checkbox_input.is_selected():
                    checkbox_input.click()
                    logging.info(f"Type checkbox '{type_name}' selected.")
                    type_selected = True

            if topic_selected and type_selected:
                break

        if topic_name and not topic_selected:
            logging.warning(f"Checkbox element not found for topic '{topic_name}'.")
        if type_name and not type_selected:
            logging.warning(f"Checkbox element not found for type '{type_name}'.")
        logging.info("News topic and type selected successfully.")

    except Exception as e:
        logging.error(f"Error in select_topic_type: {str(e)}")


def sort_by(driver, params):
    try:
        if not params["sort_by"]:
            logging.warning("No sort by option specified.")
            return

        sort_by_value = params["sort_by"]
        select = Select(driver.find_element(By.CLASS_NAME, "select-input"))
        select.select_by_visible_text(sort_by_value)
        logging.info(f"Option '{sort_by_value}' selected in the sort by dropdown.")

    except Exception as e:
        logging.error(f"Error in sort_by: {str(e)}")
        raise e
