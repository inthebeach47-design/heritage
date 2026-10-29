import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent


class StaticSiteHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean_path = unquote(urlparse(path).path).lstrip("/")
        translated = (ROOT / clean_path).resolve()
        try:
            translated.relative_to(ROOT)
        except ValueError:
            return str(ROOT / "index.html")
        if translated.is_dir():
            index = translated / "index.html"
            if index.exists():
                return str(index)
        if translated.exists():
            return str(translated)
        return str(ROOT / "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("127.0.0.1", port), StaticSiteHandler)
    print(f"Serving Heritage Mabati export at http://127.0.0.1:{port}")
    server.serve_forever()
