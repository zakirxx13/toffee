import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# =========================================================
# CONFIG
# =========================================================

SOURCE_URL = "https://example.com/"
OUTPUT_FILE = "playlist.m3u8"

REQUEST_TIMEOUT = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# =========================================================
# SESSION
# =========================================================

def create_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


# =========================================================
# FETCH PAGE
# =========================================================

def fetch_page(session, url):
    print("Fetching source page...")
    print(url)

    response = session.get(
        url,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True
    )

    response.raise_for_status()

    print(
        "HTTP Status:",
        response.status_code
    )

    print(
        "Final URL:",
        response.url
    )

    return response


# =========================================================
# PAGE TITLE
# =========================================================

def get_page_title(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    title = soup.find("title")

    if title:
        value = title.get_text(
            " ",
            strip=True
        )

        if value:
            return value

    return "Demo Channel"


# =========================================================
# FIND PUBLIC M3U8 URLS
# =========================================================

def find_m3u8_urls(html, base_url):
    found = []

    # Direct URLs inside HTML
    matches = re.findall(
        r'https?://[^\s"\'<>]+?\.m3u8(?:\?[^\s"\'<>]*)?',
        html,
        re.IGNORECASE
    )

    for url in matches:
        url = url.replace(
            "\\/",
            "/"
        )

        found.append(url)

    # Relative .m3u8 paths
    relative_matches = re.findall(
        r'["\']([^"\']+\.m3u8(?:\?[^"\']*)?)["\']',
        html,
        re.IGNORECASE
    )

    for url in relative_matches:
        url = url.replace(
            "\\/",
            "/"
        )

        absolute_url = urljoin(
            base_url,
            url
        )

        found.append(
            absolute_url
        )

    # Remove duplicates
    unique_urls = list(
        dict.fromkeys(found)
    )

    return unique_urls


# =========================================================
# FIND VIDEO / SOURCE ELEMENTS
# =========================================================

def find_media_sources(html, base_url):
    soup =
