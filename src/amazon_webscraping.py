# -*- coding: utf-8 -*-

"""Amazon Webscraping."""

# Modules
import re
import time
from datetime import datetime

import bs4
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

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

# ERASE
path_to_wishlist = r".\files\wishlist\my_shopping_list.csv"
path_to_history = r".\files\results\my_shoppin_list_searched.csv"


# Private function _get_price_tag
def _get_price_tag(soup: BeautifulSoup) -> bs4.element.Tag:
    """[summary].

    Args:
        soup (BeautifulSoup): [description]

    Returns:
        bs4.element.Tag: [description]
    """
    price_tag_class = "a-price a-text-price a-size-medium apexPriceToPay"
    price_tag = soup.find(id="priceblock_ourprice")
    if not price_tag:
        price_tag = soup.find(id="priceblock_saleprice")
        if not price_tag:
            price_tag = soup.find("span", {"data-a-color": "price"})
            if price_tag:
                price_class = {"class": "a-offscreen"}
                price_tag = price_tag.find("span", price_class)
            else:
                price_tags = soup.find_all("span", {"class": price_tag_class})
                if price_tags:
                    price_tag = price_tags[-1]
                    if price_tag:
                        price_class = {"class": "a-offscreen"}
                        price_tag = price_tag.find("span", price_class)
    return price_tag


# End of function _get_price_tag

# Function search_product_list
def search_product_list(
    path_to_wishlist: str,
    path_to_history: str,
) -> None:
    """[summary].

    Args:
        path_to_wishlist (str): [description]
        path_to_history (str): [description]
    """
    prod_tracker = pd.read_csv(path_to_wishlist)
    prod_tracker_urls = prod_tracker["url"]
    now = datetime.now().strftime("%Y-%m-%d %Hh%Mm")
    list_url_info = []
    for index_, url in enumerate(prod_tracker_urls):
        if index_ >= 1:
            time.sleep(5)
        url_info = {
            "date": now.replace("h", ":").replace("m", ""),
            "code": prod_tracker["code"][index_],
            "url": url,
            "buy_below": prod_tracker["buy_below"][index_],
        }
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
            continue
        retries = 0
        soup = BeautifulSoup(page.content, features="lxml")
        # Check for robot detection
        robot = soup.find("p", {"class": "a-last"})
        while retries < 3:
            if robot:
                robot_text = robot.get_text()
                if robot_text.startswith("Sorry, we just need to make sure"):
                    retries += 1
                    time.sleep(30 + 10 * retries)
                    page = requests.get(url, headers=HEADERS)
                    soup = BeautifulSoup(page.content, features="lxml")
                    robot = soup.find("p", {"class": "a-last"})
            else:
                break
        if retries >= 3:
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
        url_info["price"] = url_info.get("price", np.nan)
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
            # if there is any error in the previous try statements,
            # it means the product is available
            stock = "Available"
            url_info["stock"] = stock
        url_info["stock"] = url_info.get("stock", "")
        # Getting dataframe
        list_url_info.append(url_info)
        if (not np.isnan(url_info.get("price"))) & (
            url_info.get("price") < url_info.get("buy_below")
        ):
            print(
                "".join(
                    [
                        "************************ ALERT! ",
                        f"BUY {prod_tracker.code[index_]}",
                        " ************************",
                    ]
                )
            )
    # after the run, checks last search history record,
    # and appends this run results to it, saving a new file
    tracker_log = pd.DataFrame(list_url_info)
    tracker_log.to_csv(path_to_history, mode="a", header=False, index=False)


# End of function search_product_list

if __name__ == "__main__":
    search_product_list(path_to_wishlist, path_to_history)
