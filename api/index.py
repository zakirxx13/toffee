from http.server import BaseHTTPRequestHandler
from pathlib import Path


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            playlist_file = Path("playlist.m3u8")

            if not playlist_file.exists():
                self.send_response(404)
                self.send_header(
                    "Content-Type",
                    "text/plain; charset=utf-8"
                )
                self.end_headers()
                self.wfile.write(
                    b"Playlist not generated yet."
                )
                return

            content = playlist_file.read_text(
                encoding="utf-8"
            )

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/vnd.apple.mpegurl"
            )
            self.send_header(
                "Cache-Control",
                "no-cache"
            )
            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )
            self.end_headers()

            self.wfile.write(
                content.encode("utf-8")
            )

        except Exception as error:
            self.send_response(500)
            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(
                str(error).encode("utf-8")
            )
