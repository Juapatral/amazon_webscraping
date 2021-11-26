# -*- coding: utf-8 -*-

"""Amazon Webscraping."""

# Modules
import logging
import os
import re
import sys
import time
from datetime import datetime

import bs4
import numpy as np
import pandas as pd
import pywhatkit
import requests

# Constants
HEADERS = {
    "User-Agent": "".join(
        [
            "Mozilla/5.0 (Windows NT 6.1) ",
            "AppleWebKit/537.36 (KHTML, like Gecko) ",
            "Chrome/41.0.2228.0 ",
            "Safari/537.36",
        ]
    ),
    "Accept-Language": "en-US, en;q=0.5",
}

# Log cofiguration
logging.basicConfig(format="[%(asctime)s]: %(message)s", level=logging.INFO)


# Private function _get_price_tag
def _get_price_tag(soup: bs4.BeautifulSoup) -> bs4.element.Tag:
    """Get price tag from multiple possible tags.

    Args:
        soup (bs4.BeautifulSoup): Soup from an amazon article.

    Returns:
        bs4.element.Tag: Tag with price
    """
    price_tag_class = "a-price a-text-price a-size-medium apexPriceToPay"
    price_tag = soup.find(id="priceblock_ourprice")
    if not price_tag:
        price_tag = soup.find(id="priceblock_saleprice")
        if not price_tag:
            price_tag = soup.find("span", {"data-a-color": "price"})
            if price_tag:
                price_tag = price_tag.find("span", {"class": "a-offscreen"})
            else:
                price_tags = soup.find_all("span", {"class": price_tag_class})
                if price_tags:
                    price_tag = price_tags[-1]
                    if price_tag:
                        price_class = {"class": "a-offscreen"}
                        price_tag = price_tag.find("span", price_class)
    return price_tag


# End of function _get_price_tag


# Private Function _send_whatsapp
def _send_whatsapp(number: str, url_info: dict):
    """Send a whatsapp message using Whatsapp web.

    Args:
        number (str): Phone number to send message with country code.
        message (str): Message.
    """
    # Define message
    message = "".join(
        [
            "Soy un bot que busca productos de Amazon y te comento que ",
            f"""tu producto: {url_info.get("code", "PROD_CODE")}. """,
            "está a 5 USD de diferencia de: ",
            f"""{url_info.get("buy_below")}. """,
            f"""Esta es la URL: {url_info.get("url","URL_PRODUCTO")}""",
        ]
    )
    # Send whatsapp

    pywhatkit.sendwhatmsg_instantly(
        number, message, wait_time=10, tab_close=True, close_time=5
    )


# End of private function _send_whatsapp

# Function search_product_list
def search_product_list(
    path_to_wishlist: str,
    path_to_history: str,
    path_to_users: str,
) -> None:
    """[summary].

    Args:
        path_to_wishlist (str): [description]
        path_to_history (str): [description]
    """
    # Load information
    logging.info("# ------- READING FILES ------- #")
    prod_tracker = pd.read_csv(path_to_wishlist)
    users_details = pd.read_csv(path_to_users)

    # Merge user information
    prod_tracker = prod_tracker.merge(users_details)

    # Get urls and dates
    prod_tracker_urls = prod_tracker["url"]
    now = datetime.now().strftime("%Y-%m-%d %Hh%Mm")

    # Iterate over each url
    list_url_info = []
    logging.info("Starting scraping of product...")
    for index_, url in enumerate(prod_tracker_urls):
        # After first url, wait 5 seconds between.
        if index_ >= 1:
            time.sleep(5)

        # Create url information dictionary
        url_info = {
            "date": now.replace("h", ":").replace("m", ""),
            "user": prod_tracker["user"][index_],
            "code": prod_tracker["code"][index_],
            "url": url,
            "buy_below": prod_tracker["buy_below"][index_],
        }
        code = url_info["code"]

        # Request
        retries = 0
        page = requests.get(url, headers=HEADERS)

        # Check for good response
        while retries < 5:
            if page.status_code != 200:
                retries += 1
                time.sleep(10)
                page = requests.get(url, headers=HEADERS)
            else:
                break
        if retries >= 5:
            logging.warning(f"Product {code} did not retrieve information.")
            continue
        retries = 0
        soup = bs4.BeautifulSoup(page.content, features="lxml")

        # Check for robot detection
        robot = soup.find("p", {"class": "a-last"})
        while retries < 3:
            if robot:
                robot_text = robot.get_text()
                if robot_text.startswith("Sorry, we just need to make sure"):
                    retries += 1
                    seconds = 30 + 10 * retries
                    logging.warning(
                        "".join(
                            [
                                f"Robot detection, waiting for {seconds} ",
                                "seconds.",
                            ]
                        )
                    )
                    time.sleep(seconds)
                    page = requests.get(url, headers=HEADERS)
                    soup = bs4.BeautifulSoup(page.content, features="lxml")
                    robot = soup.find("p", {"class": "a-last"})
            else:
                break
        if retries >= 3:
            logging.error(f"Too many robot detection for product {code}.")
            continue

        # Title
        title_tag = soup.find(id="productTitle")
        if title_tag:
            title = title_tag.get_text().strip()
            url_info["title"] = title
        url_info["title"] = url_info.get("title", "")

        # Price
        price_tag = _get_price_tag(soup)
        if price_tag:
            price = float(
                price_tag.get_text()
                .replace("US", "")
                .replace("\xa0", "")
                .replace("$", "")
                .replace(",", "")
                .strip()
            )
            url_info["price"] = price
            url["price_difference"] = price - url.get("buy_below")
        url_info["price"] = url_info.get("price", np.nan)
        url_info["price_difference"] = url_info.get("price_difference", np.nan)

        # Review count
        review_count_tag = soup.find(id="acrCustomerReviewText")
        if review_count_tag:
            review_count = int(
                review_count_tag.get_text()
                .split(" ")[0]
                .replace(".", "")
                .replace(",", "")
            )
            url_info["review_count"] = review_count
        url_info["review_count"] = url_info.get("review_count", np.nan)

        # Review score
        review_score_class = "i[class*='a-icon a-icon-star a-star-']"
        review_score_tag = soup.select(review_score_class)
        if review_score_tag != []:
            for score_tag in review_score_tag:
                try:
                    review_score = float(
                        score_tag.get_text().split(" ")[0].replace(",", ".")
                    )
                    url_info["review_score"] = review_score
                    break
                except (AttributeError, KeyError):
                    continue
        url_info["review_score"] = url_info.get("review_score", np.nan)

        # checking if there is "Out of stock"
        try:
            available = soup.select("#availability .a-color-price")
            if available != []:
                quantity = (
                    available[0]
                    .get_text()
                    .strip()
                    .lower()
                    .replace(".", "")
                    .replace(",", "")
                )
                if re.search("[1-9]+|in stock", quantity):
                    stock = "Available"
                    url_info["stock"] = stock
                else:
                    stock = "Out of stock"
                    url_info["stock"] = stock
            else:
                stock = "Available"
                url_info["stock"] = stock
        except (AttributeError, IndexError):
            # Ff any error the product is available
            stock = "Available"
            url_info["stock"] = stock
        url_info["stock"] = url_info.get("stock", "")

        # Getting dataframe
        list_url_info.append(url_info)

        # WARNING
        if (not np.isnan(url_info.get("price_difference", np.nan))) & (
            url_info.get("price_difference", 99999) < 4.99
        ):
            logging.info("Product {code} might be ready to buy.")
            number = "".join(["+", str(prod_tracker["phone"][index_])])
            _send_whatsapp(number, url_info)

    # Append this run results
    tracker_log = pd.DataFrame(list_url_info)
    size = tracker_log.shape[0]
    logging.info(f"Scraper finished. Extracted {size} products.")
    tracker_log.to_csv(path_to_history, mode="a", header=False, index=False)


# End of function search_product_list

if __name__ == "__main__":

    if len(sys.argv) < 4:
        logging.error("Not enough files provided.")
        raise RuntimeError("You must add path to files.")

    files_list = sys.argv

    path_to_wishlist = files_list[1]
    path_to_users = files_list[2]
    path_to_history = files_list[3]

    if not os.path.isdir(path_to_wishlist):
        logging.error(f"File {path_to_wishlist} does not exists.")
        raise RuntimeError(f"File {path_to_wishlist} does not exists.")

    if not os.path.isdir(path_to_users):
        logging.error(f"File {path_to_users} does not exists.")
        raise RuntimeError(f"File {path_to_users} does not exists.")

    if not os.path.isdir(path_to_history):
        logging.warning(f"File {path_to_history} does not exists.")
        logging.warning("It will be created")

    search_product_list(path_to_wishlist, path_to_history, path_to_users)
