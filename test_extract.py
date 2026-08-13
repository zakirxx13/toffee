import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


TARGET_URL = "https://toffeelive.com/en/watch/wHLVIJ4B7a1HdMSjaGLJ"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def inspect_page(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    print("Status:", response.status_code)
    print("Final URL:", response.url)
    print("Content-Type:", response.headers.get("Content-Type"))

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    print("\nTitle:")

    title = soup.find("title")

    if title:
        print(title.get_text(" ", strip=True))
    else:
        print("No title found")

    print("\nIframes:")

    iframe_count = 0

    for iframe in soup.find_all("iframe", src=True):
        src = iframe.get("src", "").strip()

        if src:
            iframe_count += 1
            print(
                iframe_count,
                urljoin(response.url, src)
            )

    if iframe_count == 0:
        print("No iframe found")

    print("\nVideo Sources:")

    video_count = 0

    for tag in soup.find_all(
        ["video", "source"],
        src=True
    ):
        src = tag.get("src", "").strip()

        if src:
            video_count += 1
            print(
                video_count,
                urljoin(response.url, src)
            )

    if video_count == 0:
        print("No direct video source found")


if __name__ == "__main__":
    print("Inspecting target page...")
    inspect_page(TARGET_URL)
