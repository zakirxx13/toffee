import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


TARGET_URL = "https://toffeelive.com/en/watch/wHLVIJ4B7a1HdMSjaGLJ"

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
    "Accept-Language": "en-US,en;q=0.9"
}


def scrape(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20,
        allow_redirects=True
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    print("Status:", response.status_code)
    print("Final URL:", response.url)

    print("\n--- IFRAME SOURCES ---")

    for iframe in soup.find_all(
        "iframe",
        src=True
    ):
        src = iframe.get("src", "").strip()

        if src:
            print(
                urljoin(response.url, src)
            )

    print("\n--- SCRIPT SOURCES ---")

    for script in soup.find_all(
        "script",
        src=True
    ):
        src = script.get("src", "").strip()

        if src:
            print(
                urljoin(response.url, src)
            )

    print("\n--- VIDEO SOURCES ---")

    for tag in soup.find_all(
        ["video", "source"],
        src=True
    ):
        src = tag.get("src", "").strip()

        if src:
            print(
                urljoin(response.url, src)
            )


if __name__ == "__main__":
    scrape(TARGET_URL)
