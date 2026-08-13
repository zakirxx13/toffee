import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://toffeelive.com/en/watch/wHLVIJ4B7a1HdMSjaGLJ"
OUTPUT_FILE = "playlist.m3u8"

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


def fetch_page(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20,
        allow_redirects=True
    )

    response.raise_for_status()

    return response


def extract_media_sources(html, base_url):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    sources = []

    for tag in soup.find_all(
        ["video", "source"],
        src=True
    ):
        src = tag.get("src", "").strip()

        if not src:
            continue

        sources.append(
            urljoin(base_url, src)
        )

    return list(dict.fromkeys(sources))


def create_playlist(title, sources):
    lines = [
        "#EXTM3U"
    ]

    for index, url in enumerate(
        sources,
        start=1
    ):
        channel_name = (
            title
            if title
            else f"Demo Channel {index}"
        )

        lines.append(
            '#EXTINF:-1 '
            f'tvg-name="{channel_name}" '
            'group-title="Demo",'
            f'{channel_name}'
        )

        lines.append(url)

    return "\n".join(lines) + "\n"


def generate_playlist():
    print("Fetching source page...")

    response = fetch_page(
        SOURCE_URL
    )

    print(
        "HTTP Status:",
        response.status_code
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    title_tag = soup.find("title")

    title = ""

    if title_tag:
        title = title_tag.get_text(
            " ",
            strip=True
        )

    sources = extract_media_sources(
        response.text,
        response.url
    )

    playlist = create_playlist(
        title,
        sources
    )

    Path(OUTPUT_FILE).write_text(
        playlist,
        encoding="utf-8"
    )

    print(
        f"Playlist saved: {OUTPUT_FILE}"
    )

    print(
        "Media sources found:",
        len(sources)
    )


if __name__ == "__main__":
    generate_playlist()
