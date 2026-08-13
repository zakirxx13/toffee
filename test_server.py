import os
import sys
import threading
import time

import requests
from http.server import HTTPServer

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "api"
    )
)

from index import handler


HOST = "127.0.0.1"
PORT = 8081


def test_fetch():
    time.sleep(1)

    url = f"http://{HOST}:{PORT}/playlist.m3u8"

    print("Fetching:", url)

    try:
        response = requests.get(
            url,
            timeout=15
        )

        print(
            "Response Code:",
            response.status_code
        )

        print(
            "Content-Type:",
            response.headers.get(
                "Content-Type"
            )
        )

        print(
            "Playlist length:",
            len(response.text)
        )

        print("\nPreview:")

        print(
            "\n".join(
                response.text.splitlines()[:10]
            )
        )

    except Exception as error:
        print(
            "Test error:",
            error
        )

    finally:
        os._exit(0)


server = HTTPServer(
    (HOST, PORT),
    handler
)

threading.Thread(
    target=test_fetch,
    daemon=True
).start()

print(
    f"Server running at "
    f"http://{HOST}:{PORT}"
)

server.serve_forever()
