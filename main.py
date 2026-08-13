import json
import re
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
        "application/xml;q=0.9,image/avif,image/webp,"
        "*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


def create_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def fetch_page(session, url):
    response = session.get(
        url,
        timeout=20,
        allow_redirects=True
    )

    response.raise_for_status()

    return response


def unique(items):
    return list(dict.fromkeys(items))


def extract_metadata(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    data = {
        "title": "",
        "description": "",
        "canonical": "",
        "og_title": "",
        "og_description": "",
        "og_image": "",
        "iframes": [],
        "video_sources": [],
        "script_sources": [],
        "m3u8_references": [],
        "json_ld": []
    }

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    title = soup.find("title")

    if title:
        data["title"] = title.get_text(" ", strip=True)

    # --------------------------------------------------
    # META DESCRIPTION
    # --------------------------------------------------

    description = soup.find(
        "meta",
        attrs={"name": re.compile(r"^description$", re.I)}
    )

    if description:
        data["description"] = (
            description.get("content", "").strip()
        )

    # --------------------------------------------------
    # CANONICAL
    # --------------------------------------------------

    canonical = soup.find(
        "link",
        attrs={
            "rel": lambda value:
                value and "canonical" in value
        }
    )

    if canonical:
        data["canonical"] = urljoin(
            base_url,
            canonical.get("href", "")
        )

    # --------------------------------------------------
    # OPEN GRAPH
    # --------------------------------------------------

    og_title = soup.find(
        "meta",
        attrs={"property": "og:title"}
    )

    if og_title:
        data["og_title"] = og_title.get("content", "")

    og_description = soup.find(
        "meta",
        attrs={"property": "og:description"}
    )

    if og_description:
        data["og_description"] = (
            og_description.get("content", "")
        )

    og_image = soup.find(
        "meta",
        attrs={"property": "og:image"}
    )

    if og_image:
        data["og_image"] = urljoin(
            base_url,
            og_image.get("content", "")
        )

    # --------------------------------------------------
    # IFRAMES
    # --------------------------------------------------

    iframe_urls = []

    for iframe in soup.find_all("iframe", src=True):
        src = iframe.get("src", "").strip()

        if src:
            iframe_urls.append(
                urljoin(base_url, src)
            )

    data["iframes"] = unique(iframe_urls)

    # --------------------------------------------------
    # VIDEO / SOURCE
    # --------------------------------------------------

    video_sources = []

    for tag in soup.find_all(
        ["video", "source"],
        src=True
    ):
        src = tag.get("src", "").strip()

        if src:
            video_sources.append(
                urljoin(base_url, src)
            )

    data["video_sources"] = unique(video_sources)

    # --------------------------------------------------
    # JAVASCRIPT FILES
    # --------------------------------------------------

    script_sources = []

    for script in soup.find_all(
        "script",
        src=True
    ):
        src = script.get("src", "").strip()

        if src:
            script_sources.append(
                urljoin(base_url, src)
            )

    data["script_sources"] = unique(script_sources)

    # --------------------------------------------------
    # PUBLIC M3U8 REFERENCES
    # --------------------------------------------------
    #
    # Only searches the HTML that was already downloaded.
    # It does not decrypt, bypass DRM, or authenticate
    # against protected streaming services.
    #

    m3u8_pattern = re.compile(
        r'https?://[^\s"\'<>\\]+\.m3u8'
        r'(?:\?[^\s"\'<>\\]*)?',
        re.IGNORECASE
    )

    m3u8_matches = m3u8_pattern.findall(html)

    data["m3u8_references"] = unique(
        m3u8_matches
    )

    # --------------------------------------------------
    # JSON-LD
    # --------------------------------------------------

    for script in soup.find_all(
        "script",
        attrs={
            "type": re.compile(
                r"application/ld\+json",
                re.I
            )
        }
    ):
        raw = script.string or script.get_text()

        if not raw.strip():
            continue

        try:
            parsed = json.loads(raw)

            data["json_ld"].append(parsed)

        except (json.JSONDecodeError, TypeError):
            continue

    return data


def inspect_target(url):
    session = create_session()

    response = fetch_page(
        session,
        url
    )

    metadata = extract_metadata(
        response.text,
        response.url
    )

    result = {
        "requested_url": url,
        "final_url": response.url,
        "status_code": response.status_code,
        "content_type": response.headers.get(
            "Content-Type",
            ""
        ),
        "content_length": len(response.content),
        "metadata": metadata
    }

    return result


def save_result(result):
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


def print_summary(result):
    metadata = result["metadata"]

    print("=" * 60)
    print("STREAMING PAGE INSPECTOR")
    print("=" * 60)

    print()
    print("Requested URL:")
    print(result["requested_url"])

    print()
    print("Final URL:")
    print(result["final_url"])

    print()
    print("HTTP Status:")
    print(result["status_code"])

    print()
    print("Content-Type:")
    print(result["content_type"])

    print()
    print("Page Title:")
    print(metadata["title"] or "Not found")

    print()
    print("Description:")
    print(metadata["description"] or "Not found")

    print()
    print("Canonical:")
    print(metadata["canonical"] or "Not found")

    print()
    print("Open Graph Image:")
    print(metadata["og_image"] or "Not found")

    print()
    print("Iframes:")
    if metadata["iframes"]:
        for item in metadata["iframes"]:
            print(" -", item)
    else:
        print(" - None found")

    print()
    print("Video Sources:")
    if metadata["video_sources"]:
        for item in metadata["video_sources"]:
            print(" -", item)
    else:
        print(" - None found")

    print()
    print("M3U8 References in HTML:")
    if metadata["m3u8_references"]:
        for item in metadata["m3u8_references"]:
            print(" -", item)
    else:
        print(" - None found")

    print()
    print("JavaScript Files:")
    print(
        f" - {len(metadata['script_sources'])} found"
    )

    print()
    print("=" * 60)


def main():
    try:
        result = inspect_target(
            TARGET_URL
        )

        save_result(result)

        print_summary(result)

        print()
        print(
            "Saved: inspection_result.json"
        )

    except requests.exceptions.Timeout:
        print(
            "ERROR: Request timed out."
        )

    except requests.exceptions.HTTPError as error:
        print(
            "ERROR: HTTP request failed:",
            error
        )

    except requests.exceptions.RequestException as error:
        print(
            "ERROR: Network request failed:",
            error
        )

    except Exception as error:
        print(
            "ERROR:",
            error
        )


if __name__ == "__main__":
    main()
