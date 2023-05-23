import requests
from bs4 import BeautifulSoup
import yaml
import os
import pandas as pd
from typing import Dict, List
import time
from logzero import logger
from tqdm import tqdm
import pickle5 as pkl

ROOT_URL = "https://www.tauschwohnung.com"
LOGIN_URL = "https://www.tauschwohnung.com/login"
SEARCH_URL = "https://www.tauschwohnung.com/search/result?city={city}&housing_type=1&rooms_min=1&storey_min=-1&storey_max=10&sort=standard&page={page}"

cities = [
    "Berlin",
    "Köln",
    "München",
    "Zürich",
    "Hamburg",
    "Wien",
    "Düsseldorf",
    "Frankfurt+am+Main",
    "Stuttgart",
]

cookies = {
    "_pk_id.1.3aa3": "efce13a6140ddc5c.1683740292",
    "tauschwohnung": "f5857706a5a85b28ec1a97a517ce8e478158582b",
    "_pk_ses.1.3aa3": "%2A",
    "_pk_cvar.1.3aa3": "%5B%5D",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.tauschwohnung.com",
    "Connection": "keep-alive",
    "Referer": "https://www.tauschwohnung.com/login",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "TE": "trailers",
}

payload = yaml.safe_load("./credentials/tauschwohnung.yaml")


def login(
    login_url: str, cookies: Dict, headers: Dict, payload: Dict
) -> requests.Session:
    """Handles the login into a website in order to be able to parse it afterwards.

    A `ValueError` is raised in case the login was not performed.

    Args:
        login_url: the URL to the login page of the website
        cookies: the cookies yielded by the regular login request of the website
        headers: the headers yielded by the regular login request of the website
        payload: the credentials needed to log in (including a potential csrf token)

    Returns:
        s: a `requests.Session` object with login performed, ready to scrap
    """
    s = requests.session()
    login_req = s.post(login_url, headers=headers, cookies=cookies, data=payload)

    if login_req.status_code != 200:
        raise ValueError("Login failed")

    return s


def build_dataset(
    s: requests.Session,
    search_url: str,
    root_url: str,
    cities: List[str],
    store: bool = False,
) -> pd.DataFrame:
    """Scraps the indicated website to look for every possible ads.

    The website URLs have to follow a specific pattern described below.

    Args:
        s: requests.Session objet used to perform the requests to the website. Login is assumed to have been performed before.
        search_url: the *template* URL of a search page of the website. It has to be missing a city name (`city`) and a page number (`page`), which will be added through the `format()` method.
        root_url: the URL to which one should add the links scraped in the search page to reach the page of every ad.
        cities: the list of cities to fill the URLs with.
        store: if `True`, the list of links is locally saved to a `.pkl` file.

    Returns:
        df: a `pd.DataFrame` object containing the data with columns named as mentioned in the docs.
    """
    data = {
        "g-city": [],
        "g-rent": [],
        "g-surf": [],
        "g-rooms": [],
        "t-city": [],
        "t-max-rent": [],
        "t-surf-min": [],
        "t-rooms": [],
    }

    for city in cities:
        # Find how many pages we have to browse
        logger.debug(
            "Currently performing scraping for {city}... \n Looking for links.".format(
                city=city
            )
        )
        soup = BeautifulSoup(
            s.get(SEARCH_URL.format(city=city, page=1)).text, "html.parser"
        )
        page_links = soup.find_all("a", class_="page-link")
        max_page = int(page_links[-2].text)

        # Store the links to browse
        links = []
        logger.debug("Storing links...")
        for page in tqdm(range(1, max_page + 1)):
            soup = BeautifulSoup(
                s.get(SEARCH_URL.format(city=city, page=page)).text, "html.parser"
            )
            for link in soup.find_all(
                "a", class_="stretched-link embed-responsive embed-responsive-4by3"
            ):
                links.append(link["href"])
            time.sleep(0.1)

        if store:
            with open("./links.pickle", "wb+") as f:
                pkl.dump(links, f)
            logger.info("List of links successfully saved to a pickle file.")

        # Browse the links and store data
        logger.debug("Links found. Scraping has started.")
        for link in tqdm(links):
            soup = BeautifulSoup(s.get(ROOT_URL + link).text, "html.parser")
            strong = soup.find_all("strong")
            data["g-city"].append(city)

            try:
                data["g-rent"].append(strong[0].text)
            except IndexError:
                data["g-rent"].append("N/A")

            try:
                data["g-surf"].append(strong[1].text)
            except IndexError:
                data["g-surf"].append("N/A")

            try:
                data["g-rooms"].append(strong[2].text)
            except IndexError:
                data["g-rooms"].append("N/A")

            try:
                data["t-city"].append(strong[5].text.strip())
            except IndexError:
                data["t-city"].append("N/A")

            try:
                data["t-max-rent"].append(strong[7].text.strip())
            except IndexError:
                data["t-max-rent"].append("N/A")

            try:
                data["t-surf-min"].append(strong[8].text.strip())
            except IndexError:
                data["t-surf-min"].append("N/A")

            try:
                data["t-rooms"].append(strong[9].text.strip())
            except:
                data["t-rooms"].append("N/A")

            time.sleep(0.5)

        logger.debug("Scraping perfomed for {city}.".format(city=city))

        time.sleep(10)

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    s = login(LOGIN_URL, cookies=cookies, headers=headers, payload=payload)
    data = build_dataset(s, SEARCH_URL, ROOT_URL, cities, store=True)
    logger.info("Dataset built successfully! Saving to CSV...")
    data.to_csv("./data_tauschwohnung.csv")
