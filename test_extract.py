import requests
from bs4 import BeautifulSoup


DEMO_URL = "https://example.com/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def inspect_page(url):
    print("Fetching:", url)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    print(
        "Status:",
        response.status_code
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    print("\nPage title:")

    title = soup.find("title")

    if title:
        print(
            title.get_text(
                strip=True
            )
        )
    else:
        print("No title found.")

    print("\nVideo/source elements:")

    found = False

    for tag in soup.find_all(
        ["video", "source"]
    ):
        src = tag.get("src")

        if src:
            found = True
            print(src)

    if not found:
        print("No public video source found.")


if __name__ == "__main__":
    inspect_page(
        DEMO_URL
    )
