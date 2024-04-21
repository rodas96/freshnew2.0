import logging
import datetime
import json
from selenium import webdriver
import platform
import os
from selenium.webdriver.chrome.options import Options
from robocorp import workitems


def initilization():
    try:
        kill_chrome()
        setup_logging()
        driver = init_driver()
        params = load_params()
        logging.info("Initialization completed successfully.")
        return driver, params
    except Exception as e:
        logging.error(f"Failed in the intilization: {str(e)}")
        raise e("Failed in the intilization: " + str(e))


def setup_logging():
    log_file_name = datetime.datetime.now().strftime(
        "output/freshnews2.0_%Y-%m-%d_%H-%M.log"
    )
    logging.basicConfig(
        filename=log_file_name,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def init_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--incognito")

        driver = webdriver.Chrome(options=chrome_options)
        if not driver:
            logging.error("Failed to initialize WebDriver")
            raise Exception("Failed to initialize WebDriver")
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {str(e)}")
        raise e("Failed to initialize WebDriver")


def load_params():
    try:
        if workitems.input.current:
            params = workitems.input.current
            if not params.get("search_phrase"):
                print("No search phrase provided in params.json")
                raise ValueError("No search phrase provided in params.json")
        else:
            raise ("testing robocorp")
            with open("test1knews.json", "r") as f:
                params = json.load(f)
                if not params.get("search_phrase"):
                    raise ValueError("No search phrase provided in params.json")
        return params
    except FileNotFoundError:
        logging.error("params.json not found")
        raise FileNotFoundError("params.json not found")
    except Exception as e:
        logging.error(f"Failed to load parameters: {str(e)}")
        raise e("Failed to load parameters")


def kill_chrome():
    system = platform.system()
    if system == "Windows":
        os.system("taskkill /f /im chrome.exe")
    elif system == "Linux":
        os.system("pkill chrome")
    elif system == "Darwin":
        os.system("pkill -f 'Google Chrome'")
