import json
import re
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://toffeelive.com/en/watch/wHLVIJ4B7a1HdMSjaGLJ"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def inspect_page(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20,
        allow_redirects=True
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    result = {
        "url": url,
        "final_url": response.url,
        "status": response.status_code,
        "content_type": response.headers.get("Content-Type", ""),
        "title": "",
        "iframes": [],
        "video_sources": [],
        "m3u8_references": []
    }

    # Page title
    if soup.title:
        result["title"] = soup.title.get_text(strip=True)

    # iframe URLs
    for iframe in soup.find_all("iframe", src=True):
        result["iframes"].append(iframe["src"])

    # video/source URLs
    for tag in soup.find_all(["video", "source"], src=True):
        result["video_sources"].append(tag["src"])

    # Detect only M3U8 URLs already exposed in downloaded HTML
    matches = re.findall(
        r'https?://[^\s"\'<>]+\.m3u8(?:\?[^\s"\'<>]*)?',
        response.text,
        re.IGNORECASE
    )

    result["m3u8_references"] = list(dict.fromkeys(matches))

    return result


def main():
    print("=" * 60)
    print("Streaming Page Inspector")
    print("=" * 60)

    try:
        result = inspect_page(TARGET_URL)

        print("Status:", result["status"])
        print("Final URL:", result["final_url"])
        print("Title:", result["title"])

        print("\nIframes:")
        for item in result["iframes"]:
            print(" -", item)

        print("\nVideo sources:")
        for item in result["video_sources"]:
            print(" -", item)

        print("\nM3U8 references:")
        for item in result["m3u8_references"]:
            print(" -", item)

        with open(
            "inspection_result.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        print("\nSaved: inspection_result.json")

    except requests.RequestException as error:
        print("Request failed:", error)

    except Exception as error:
        print("Error:", error)


if __name__ == "__main__":
    main()
