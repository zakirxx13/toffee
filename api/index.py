from http.server import BaseHTTPRequestHandler
import json
import os
import sys

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
    "Accept-Language": "en-US,en;q=0.9",
}


def unique(items):
    return list(dict.fromkeys(items))


def inspect_page(url):
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

    result = {
        "requested_url": url,
        "final_url": response.url,
        "status_code": response.status_code,
        "content_type": response.headers.get(
            "Content-Type",
            ""
        ),
        "title": "",
        "description": "",
        "canonical": "",
        "og_image": "",
        "iframes": [],
        "video_sources": [],
        "script_sources": []
    }

    # Title
    title = soup.find("title")

    if title:
        result["title"] = title.get_text(
            " ",
            strip=True
        )

    # Description
    description = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    if description:
        result["description"] = (
            description.get("content", "")
        )

    # Canonical
    canonical = soup.find(
        "link",
        attrs={
            "rel": lambda value:
                value and "canonical" in value
        }
    )

    if canonical:
        result["canonical"] = urljoin(
            response.url,
            canonical.get("href", "")
        )

    # Open Graph image
    og_image = soup.find(
        "meta",
        attrs={"property": "og:image"}
    )

    if og_image:
        result["og_image"] = urljoin(
            response.url,
            og_image.get("content", "")
        )

    # Iframes
    iframe_urls = []

    for iframe in soup.find_all(
        "iframe",
        src=True
    ):
        src = iframe.get("src", "").strip()

        if src:
            iframe_urls.append(
                urljoin(response.url, src)
            )

    result["iframes"] = unique(
        iframe_urls
    )

    # Video/source URLs
    video_urls = []

    for tag in soup.find_all(
        ["video", "source"],
        src=True
    ):
        src = tag.get("src", "").strip()

        if src:
            video_urls.append(
                urljoin(response.url, src)
            )

    result["video_sources"] = unique(
        video_urls
    )

    # JavaScript files
    script_urls = []

    for script in soup.find_all(
        "script",
        src=True
    ):
        src = script.get("src", "").strip()

        if src:
            script_urls.append(
                urljoin(response.url, src)
            )

    result["script_sources"] = unique(
        script_urls
    )

    return result


class handler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        body = json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        try:
            result = inspect_page(
                TARGET_URL
            )

            self.send_json(
                200,
                {
                    "success": True,
                    "data": result
                }
            )

        except requests.exceptions.Timeout:

            self.send_json(
                504,
                {
                    "success": False,
                    "error": "Target request timed out"
                }
            )

        except requests.exceptions.HTTPError as error:

            self.send_json(
                502,
                {
                    "success": False,
                    "error": f"Target HTTP error: {error}"
                }
            )

        except requests.exceptions.RequestException as error:

            self.send_json(
                502,
                {
                    "success": False,
                    "error": f"Network error: {error}"
                }
            )

        except Exception as error:

            self.send_json(
                500,
                {
                    "success": False,
                    "error": str(error)
                }
            )


if __name__ == "__main__":
    from http.server import HTTPServer

    port = int(
        os.environ.get(
            "PORT",
            "8080"
        )
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        handler
    )

    print(
        f"API server running on port {port}"
    )

    server.serve_forever()
