import os
import sys
import threading
import time

import requests
from http.server import HTTPServer


sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "api"
    )
)

from index import handler


HOST = "127.0.0.1"
PORT = 8081


server = HTTPServer(
    (HOST, PORT),
    handler
)


def test_fetch():
    time.sleep(2)

    url = f"http://{HOST}:{PORT}"

    print(f"Fetching {url} ...")

    try:
        response = requests.get(
            url,
            timeout=30
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
            "Response Length:",
            len(response.text)
        )

        print("\nPreview:")

        print(
            response.text[:1000]
        )

    except Exception as error:
        print(
            "Test failed:",
            error
        )

    finally:
        server.shutdown()


thread = threading.Thread(
    target=test_fetch,
    daemon=True
)

thread.start()

print(
    f"Starting server on http://{HOST}:{PORT}"
)

try:
    server.serve_forever()

except KeyboardInterrupt:
    print("Server stopped.")

finally:
    server.server_close()
