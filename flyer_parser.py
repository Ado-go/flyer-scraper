import requests
import json
import argparse
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class FlyerParser:
    """
    FlyerParser is a class for scraping, parsing, and saving flyers from https://www.prospektmaschine.de website.

    This class uses `requests` and `BeautifulSoup` for basic HTML parsing and `Selenium`
    for dynamically loaded content, such as flyers from specific shops.

    Attributes:
        base_url (str): The base URL of the website containing the flyers.
        driver (selenium.webdriver.Chrome): Chrome browser instance used by Selenium.
        parsed_flyers (list): List of dictionaries containing parsed flyer information.

    Methods:
        write_flyers_to_file(file_name):
            Saves all parsed flyers to a JSON file named `file_name`.

        parse_flyers_category(category):
            Parses all shops in a given flyer category and calls `parse_category_shop`
            for each shop. Closes the Selenium driver at the end.

        parse_category_shop(shop, shop_name):
            Parses all flyers for a specific shop (`shop_name`) at the base URL + `shop`.
            Uses Selenium to handle dynamically loaded elements and calls `parse_flyer`
            for each flyer.

        parse_flyer(flyer, shop_name):
            Extracts information from a single flyer:
                - title: Flyer title
                - thumbnail: URL of the flyer image
                - shop_name: Name of the shop
                - valid_from: Start date of the flyer validity
                - valid_to: End date of the flyer validity (if available)
                - parsed_time: Timestamp when the flyer was parsed
            Stores the result in `parsed_flyers`.
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.driver = webdriver.Chrome()
        self.parsed_flyers = []

    def write_flyers_to_file(self, file_name):
        logging.info("Writing flyers data to file")
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(self.parsed_flyers, f, ensure_ascii=False, indent=4)
        except IOError as e:
            logging.error(f"Failed to write to file, Error: {e}")

    def parse_flyers_category(self, category):
        try:
            self.parsed_flyers = []
            webpage_url = self.base_url + category
            response = requests.get(webpage_url)
            logging.info(f"Website {webpage_url} has been successfully parsed")
            soup = BeautifulSoup(response.text, "html.parser")
            category_dropdown = soup.select_one(
                f'a[href="{category}"]'
            ).find_next_sibling()
            category_dropdown_links = category_dropdown.select("li > a")

            for link in category_dropdown_links:
                self.parse_category_shop(link.get("href"), link.get_text())

        except requests.RequestException as e:
            logging.error(
                f"Parsing failed: unable to get webpage at {webpage_url}, Error: {e}"
            )

        except Exception as e:
            logging.error(f"Error occured: {e}")

        finally:
            self.driver.quit()
            logging.info(
                f"Parsing completed, number of flyers parsed: {len(self.parsed_flyers)}"
            )

    def parse_category_shop(self, shop, shop_name):
        try:
            self.driver.get(self.base_url + shop)
            flyers = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        "div[id^='shop-'][id$='-brochures-prepend'] figure",
                    )
                )
            )

        except TimeoutException:
            logging.warning(f"Flyers not found for shop {shop_name}")
            return

        except Exception as e:
            logging.error(f"Error occured: {e}")

        for flyer in flyers:
            self.parse_flyer(flyer, shop_name)

        logging.info(
            f"Parsing {shop_name} flyers done, number of flyers parsed: {len(flyers)}"
        )

    def parse_flyer(self, flyer, shop_name):
        try:
            title = (
                flyer.find_element(By.TAG_NAME, "h2")
                .get_attribute("textContent")
                .strip()
            )

            thumbnail = flyer.find_element(By.TAG_NAME, "img")
            src = thumbnail.get_attribute("src") or thumbnail.get_attribute("data-src")

            flyer_validity_range = (
                flyer.find_element(By.TAG_NAME, "span")
                .get_attribute("textContent")
                .strip()
            )
            if "von" in flyer_validity_range:
                # flyer has only date from when it is valid.
                dates = flyer_validity_range.split(" ")
                valid_from = datetime.strptime(dates[2], "%d.%m.%Y").strftime(
                    "%Y-%m-%d"
                )
                valid_to = ""
            else:
                dates = flyer_validity_range.split(" - ")
                valid_from = datetime.strptime(dates[0], "%d.%m.%Y").strftime(
                    "%Y-%m-%d"
                )
                valid_to = datetime.strptime(dates[1], "%d.%m.%Y").strftime("%Y-%m-%d")

            self.parsed_flyers.append(
                {
                    "title": title,
                    "thumbnail": src,
                    "shop_name": shop_name,
                    "valid_from": valid_from,
                    "valid_to": valid_to,
                    "parsed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        except Exception as e:
            logging.error(f"Failed to parse flyer in {shop_name}, Error: {e}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Flyer scraper")

    parser.add_argument(
        "--category", default="/hypermarkte/", help="Shop category, e.g. /hypermarkte/"
    )

    parser.add_argument(
        "--output", default="parsed_flyers.json", help="Output JSON file name"
    )

    args = parser.parse_args()

    BASE_URL = "https://www.prospektmaschine.de"

    web_parser = FlyerParser(BASE_URL)
    web_parser.parse_flyers_category(args.category)
    web_parser.write_flyers_to_file(args.output)
