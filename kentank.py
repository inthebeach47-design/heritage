import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import mimetypes
import os
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlencode, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://heritagemabati.co.ke/"
OUTPUT_DIR = Path("heritage_export")
MANIFEST_PATH = OUTPUT_DIR / "site_manifest.json"
MAX_PAGES = 100
DEFAULT_WAIT_MS = 3500
DEFAULT_ASSET_WORKERS = 8
LOCAL_PHONE_COMPACT = "0751206042"
LOCAL_PHONE_DISPLAY = "0751 206 042"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TEXT_EXTENSIONS = {".css", ".html", ".js", ".json", ".map", ".svg", ".txt", ".xml"}
STATIC_EXTENSIONS = {
    ".avif",
    ".css",
    ".eot",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".js",
    ".json",
    ".map",
    ".mp4",
    ".otf",
    ".pdf",
    ".png",
    ".svg",
    ".ttf",
    ".txt",
    ".webm",
    ".webp",
    ".woff",
    ".woff2",
    ".xml",
}

ASSET_EXTENSIONS_RE = r"avif|css|eot|gif|ico|jpe?g|js|json|map|mp4|otf|pdf|png|svg|ttf|webm|webp|woff2?|xml"

TEXT_ASSET_URL_RE = re.compile(
    rf"https?:\\?/\\?/[^\"'\\s<>)]+?\\.(?:{ASSET_EXTENSIONS_RE})(?:\\?[^\"'\\s<>)]+)?",
    flags=re.IGNORECASE,
)

ROOT_RELATIVE_ASSET_URL_RE = re.compile(
    rf"(?P<quote>[\"'])/(?P<path>[^\"']+?\.(?:{ASSET_EXTENSIONS_RE})(?:\?[^\"']*)?)(?P=quote)",
    flags=re.IGNORECASE,
)

COMMON_ASSET_BASES = (
    "https://heritagemabati.co.ke/cdn/",
    "https://heritagemabati.co.ke/cdn/shop/",
)

BLOCKED_MARKERS = (
    "Checking your browser before accessing",
    "Verifying that you are not a robot",
    "/hcdn-cgi/jschallenge",
    "Please wait for up to 5 seconds",
    "<title> 403 Forbidden",
    "Access to this resource on the server is denied",
)

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


@dataclass
class PageResult:
    url: str
    html: str
    title: str


def ensure_dirs(clean: bool = True) -> None:
    if clean and OUTPUT_DIR.exists():
        backup = OUTPUT_DIR.with_name(f"{OUTPUT_DIR.name}_backup_{time.strftime('%Y%m%d_%H%M%S')}")
        try:
            OUTPUT_DIR.rename(backup)
        except OSError as exc:
            raise RuntimeError(
                f"Could not prepare a clean export because {OUTPUT_DIR} is locked. "
                "Close any server, editor preview, or Explorer window using it, or rerun with --keep."
            ) from exc
        print(f"[INFO] Previous export moved to: {backup}", flush=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_url(url: str) -> str:
    absolute = urljoin(BASE_URL, url)
    parsed = urlparse(absolute)
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)))
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", query, ""))


def same_host(url: str, base_url: str = BASE_URL) -> bool:
    return urlparse(clean_url(url)).netloc.lower() == urlparse(base_url).netloc.lower()


def extension_for_url(url: str) -> str:
    return Path(urlparse(url).path).suffix.lower()


def is_probably_blocked(html: str) -> bool:
    return any(marker in html for marker in BLOCKED_MARKERS)


def is_static_asset(url: str) -> bool:
    path = urlparse(url).path
    return bool(path) and extension_for_url(path) in STATIC_EXTENSIONS


def is_captureable_response(url: str, content_type: str) -> bool:
    if is_static_asset(url):
        return True
    lowered = content_type.lower()
    return any(
        marker in lowered
        for marker in (
            "text/css",
            "javascript",
            "application/json",
            "image/",
            "font/",
            "video/",
        )
    )


def page_path_for_url(url: str) -> Path:
    parsed = urlparse(clean_url(url))
    path = parsed.path.strip("/")
    if not path:
        return OUTPUT_DIR / "index.html"

    if Path(path).suffix:
        return OUTPUT_DIR / path

    return OUTPUT_DIR / path / "index.html"


def asset_path_for_url(url: str) -> Path:
    parsed = urlparse(clean_url(url))
    host = parsed.netloc.replace(":", "_")
    path = parsed.path.lstrip("/") or "index"
    if parsed.query:
        digest = re.sub(r"[^a-zA-Z0-9_-]+", "-", parsed.query).strip("-")[:70]
        suffix = Path(path).suffix
        stem = path[: -len(suffix)] if suffix else path
        path = f"{stem}.{digest}{suffix}"
    return OUTPUT_DIR / "assets" / host / path


def asset_alias_path_for_url(url: str) -> Path | None:
    parsed = urlparse(clean_url(url))
    if not parsed.query:
        return None
    host = parsed.netloc.replace(":", "_")
    path = parsed.path.lstrip("/") or "index"
    return OUTPUT_DIR / "assets" / host / path


def asset_dir_path_for_url(url: str) -> Path:
    parsed = urlparse(clean_url(url))
    host = parsed.netloc.replace(":", "_")
    path = parsed.path.lstrip("/")
    return OUTPUT_DIR / "assets" / host / path


def relative_url(from_file: Path, to_file: Path) -> str:
    return Path(os.path.relpath(to_file.resolve(), from_file.parent.resolve())).as_posix()


def safe_relative_url(from_file: Path, to_file: Path) -> str:
    return relative_url(from_file, to_file)


def site_root_relative_url(to_file: Path) -> str:
    return to_file.resolve().relative_to(OUTPUT_DIR.resolve()).as_posix()


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def write_asset_bytes(url: str, path: Path, content: bytes) -> None:
    write_bytes(path, content)
    alias = asset_alias_path_for_url(url)
    if alias and alias != path:
        write_bytes(alias, content)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


ROOFING_PRODUCTS = (
    ("box-profile-mabati", "Box Profile Mabati"),
    ("bricktile", "Bricktile Roofing Sheets"),
    ("corrugated-roofing-sheet", "Corrugated Roofing Sheets"),
    ("dekatile-stone-coate", "Dekatile Stone Coated Sheets"),
    ("euro-tile-roofing-sheet", "Euro Tile Roofing Sheets"),
    ("it5-roofing-mabati", "IT5 Industrial Trough Sheets"),
    ("roman-tile-roofing-sheets", "Roman Tile Roofing Sheets"),
    ("zee-tile", "Zee Tile Roofing Sheets"),
)


def customize_export() -> None:
    """Make the static export easy to browse and order from by phone or WhatsApp."""
    whatsapp_number = "254751206042"
    phone_number = "+254751206042"
    order_panel_css = """
.hm-easy-order { display:flex; flex-wrap:wrap; gap:12px; margin:20px 0; }
.hm-easy-order a { min-height:54px; padding:14px 22px; border-radius:10px; display:inline-flex;
  align-items:center; justify-content:center; font-size:18px; font-weight:800; text-decoration:none; }
.product-form-component .product-form-buttons, sticky-add-to-cart, .sticky-add-to-cart,
.shopify-payment-button, shopify-accelerated-checkout,
.header-actions__action.action__cart { display:none !important; }
.hm-easy-order__wa { background:#138443; color:#fff !important; }
.hm-easy-order__call { background:#123d69; color:#fff !important; }
.hm-order-dock { position:fixed; z-index:10000; bottom:0; left:0; right:0; display:flex; gap:12px;
  padding:12px max(16px, env(safe-area-inset-right)) calc(12px + env(safe-area-inset-bottom)) max(16px, env(safe-area-inset-left));
  background:#fff; box-shadow:0 -4px 18px rgba(15,35,55,.18); }
.hm-order-dock a { flex:1; min-height:56px; border-radius:10px; display:flex; align-items:center;
  justify-content:center; text-align:center; font-size:18px; line-height:1.2; font-weight:800; text-decoration:none; }
.hm-order-dock__wa { background:#138443; color:#fff !important; }
.hm-order-dock__call { background:#123d69; color:#fff !important; }
body { padding-bottom:88px !important; }
.hm-home-roofing { padding:44px 24px 52px; max-width:1320px; margin:auto; }
.hm-home-roofing__intro { max-width:780px; margin:0 auto 28px; text-align:center; }
.hm-home-roofing__intro h2 { margin:0 0 10px; font-size:clamp(30px,4vw,42px); line-height:1.15; }
.hm-home-roofing__intro p { margin:0; font-size:18px; line-height:1.55; }
.hm-roof-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:20px; }
.hm-roof-card { overflow:hidden; border:1px solid #dce3e9; border-radius:14px; background:#fff; box-shadow:0 5px 18px rgba(16,38,58,.08); }
.hm-roof-card__image { width:100%; height:220px; object-fit:cover; background:#f4f6f8; display:block; }
.hm-roof-card__body { padding:18px; }
.hm-roof-card h3 { margin:0 0 8px; font-size:20px; line-height:1.3; }
.hm-roof-card p { margin:0 0 16px; font-size:16px; line-height:1.45; }
.hm-roof-card__actions { display:grid; grid-template-columns:1fr 1fr; gap:9px; }
.hm-roof-card__actions a { min-height:48px; display:flex; align-items:center; justify-content:center; text-align:center;
  padding:8px; border-radius:8px; font-weight:800; text-decoration:none; }
.hm-roof-card__view { background:#eef2f6; color:#18344e !important; }
.hm-roof-card__order { background:#138443; color:#fff !important; }
@media(max-width:900px){.hm-roof-grid{grid-template-columns:repeat(2,minmax(0,1fr));}}
@media(max-width:540px){.hm-home-roofing{padding:30px 14px 36px}.hm-roof-grid{gap:12px}.hm-roof-card__image{height:155px}.hm-roof-card__body{padding:13px}.hm-roof-card h3{font-size:17px}.hm-roof-card p{font-size:15px}.hm-roof-card__actions{grid-template-columns:1fr}.hm-order-dock a{font-size:16px;min-height:52px}}
"""

    for html_path in OUTPUT_DIR.rglob("*.html"):
        try:
            soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
        except OSError:
            continue

        for previous in soup.select(".hm-easy-order, .hm-order-dock, #hm-order-panel-styles"):
            previous.decompose()

        # Replace cart purchase controls with direct ordering on product pages.
        if html_path.parent.parent == OUTPUT_DIR / "products":
            form = soup.select_one("product-form-component form.shopify-product-form")
            if form:
                for control in form.select(".product-form-buttons, shopify-accelerated-checkout, .shopify-payment-button"):
                    control.decompose()
                product_title = soup.select_one('meta[property="og:title"]')
                title = product_title.get("content", "roofing sheets") if product_title else "roofing sheets"
                title = title.split("|")[0].strip()
                panel = soup.new_tag("div", attrs={"class": "hm-easy-order"})
                wa = soup.new_tag("a", href=f"https://wa.me/{whatsapp_number}?text={quote('Hello, I would like to order ' + title + '. Please help me with price, colour, length, quantity and delivery.')}" )
                wa["class"] = "hm-easy-order__wa"
                wa.string = "Order on WhatsApp"
                call = soup.new_tag("a", href=f"tel:{phone_number}")
                call["class"] = "hm-easy-order__call"
                call.string = "Call to Order: 0751 206 042"
                panel.append(wa)
                panel.append(call)
                form.insert_after(panel)

        # Make every page offer the two clear order paths, with large touch targets.
        old_float = soup.select_one("a.heritage-whatsapp")
        if old_float:
            old_float.decompose()
        dock = soup.new_tag("nav", attrs={"class": "hm-order-dock", "aria-label": "Order by phone or WhatsApp"})
        dock_wa = soup.new_tag("a", href=f"https://wa.me/{whatsapp_number}?text={quote('Hello Heritage Mabati, I need help with an order.')}" )
        dock_wa["class"] = "hm-order-dock__wa"
        dock_wa.string = "WhatsApp: 0751 206 042"
        dock_call = soup.new_tag("a", href=f"tel:{phone_number}")
        dock_call["class"] = "hm-order-dock__call"
        dock_call.string = "Call: 0751 206 042"
        dock.append(dock_wa)
        dock.append(dock_call)
        if soup.body:
            soup.body.append(dock)
        if soup.head:
            style = soup.new_tag("style", id="hm-order-panel-styles")
            style.string = order_panel_css
            soup.head.append(style)

        # Replace the horizontal homepage carousel with all eight roofing sheet types.
        showcase = soup.select_one("#HeritageShowcase-template--26797119209774__heritage_product_slider_LJN9NR, .hm-home-roofing")
        if showcase:
            showcase.clear()
            showcase["class"] = ["hm-home-roofing"]
            intro = soup.new_tag("header", attrs={"class": "hm-home-roofing__intro"})
            heading = soup.new_tag("h2")
            heading.string = "Choose Your Roofing Sheets"
            intro.append(heading)
            intro_text = soup.new_tag("p")
            intro_text.string = "See all our roofing sheet styles in one place. Tap WhatsApp to order or call us for help choosing."
            intro.append(intro_text)
            showcase.append(intro)
            grid = soup.new_tag("div", attrs={"class": "hm-roof-grid"})
            for handle, display_name in ROOFING_PRODUCTS:
                product_path = OUTPUT_DIR / "products" / handle / "index.html"
                product_soup = BeautifulSoup(product_path.read_text(encoding="utf-8"), "html.parser") if product_path.exists() else None
                image_meta = product_soup.select_one('meta[property="og:image"]') if product_soup else None
                source_image = image_meta.get("content", "") if image_meta else ""
                if source_image.startswith("http://"):
                    source_image = "https://" + source_image[len("http://"):]
                image_local = asset_alias_path_for_url(source_image) if source_image else None
                image_href = relative_url(OUTPUT_DIR / "index.html", image_local) if image_local and image_local.exists() else source_image
                card = soup.new_tag("article", attrs={"class": "hm-roof-card"})
                product_link = soup.new_tag("a", href=f"products/{handle}/index.html", attrs={"aria-label": f"View {display_name}"})
                image = soup.new_tag("img", src=image_href, alt=display_name, attrs={"class": "hm-roof-card__image", "loading": "lazy"})
                product_link.append(image)
                card.append(product_link)
                body = soup.new_tag("div", attrs={"class": "hm-roof-card__body"})
                card_title = soup.new_tag("h3")
                card_title.string = display_name
                body.append(card_title)
                description = soup.new_tag("p")
                description.string = "Ask us for the price and help choosing the right length, colour and quantity."
                body.append(description)
                actions = soup.new_tag("div", attrs={"class": "hm-roof-card__actions"})
                view = soup.new_tag("a", href=f"products/{handle}/index.html")
                view["class"] = "hm-roof-card__view"
                view.string = "Details"
                order = soup.new_tag("a", href=f"https://wa.me/{whatsapp_number}?text={quote('Hello, I would like to order ' + display_name + '. Please help me with price, colour, length, quantity and delivery.')}", attrs={"target": "_blank", "rel": "noopener"})
                order["class"] = "hm-roof-card__order"
                order.string = "WhatsApp Order"
                actions.append(view)
                actions.append(order)
                body.append(actions)
                card.append(body)
                grid.append(card)
            showcase.append(grid)
        html_path.write_text(str(soup), encoding="utf-8")


def request_url(url: str, timeout: int = 30) -> requests.Response:
    response = SESSION.get(url, timeout=timeout, allow_redirects=True)
    response.raise_for_status()
    return response


def launch_chromium(playwright):
    """Prefer Playwright's browser, then use a Chromium already on the system."""
    try:
        return playwright.chromium.launch(headless=True)
    except Exception as managed_error:
        for executable in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
            executable_path = shutil.which(executable)
            if not executable_path:
                continue
            try:
                print(f"[INFO] Using system browser: {executable_path}", flush=True)
                return playwright.chromium.launch(headless=True, executable_path=executable_path)
            except Exception as system_error:
                raise RuntimeError(
                    f"Found {executable_path}, but Playwright could not start it. "
                    "Install Playwright's matching Chromium with `python3 -m playwright install chromium`. "
                    f"Browser error: {system_error}"
                ) from system_error

        raise RuntimeError(
            "No Chromium browser is available. Install one with "
            "`python3 -m playwright install chromium`, then run this script again."
        ) from managed_error


def fetch_rendered_pages(urls: list[str], wait_ms: int = DEFAULT_WAIT_MS) -> list[PageResult]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Install Playwright and its Chromium browser to render pages: "
            "pip install playwright && playwright install chromium"
        ) from exc

    results: list[PageResult] = []
    with sync_playwright() as playwright:
        browser = launch_chromium(playwright)
        page = browser.new_page()
        for url in urls:
            print(f"[INFO] Browser rendering: {url}")
            try:
                page.goto(url, wait_until="networkidle", timeout=90_000)
            except Exception:
                page.goto(url, wait_until="domcontentloaded", timeout=90_000)
            page.wait_for_timeout(wait_ms)
            for _ in range(6):
                if not is_probably_blocked(page.content()):
                    break
                page.wait_for_timeout(3000)
            try:
                page.wait_for_load_state("networkidle", timeout=15_000)
            except Exception:
                pass
            results.append(PageResult(url=page.url, html=page.content(), title=page.title()))
        browser.close()
    return results


class BrowserRenderer:
    def __init__(self, wait_ms: int = DEFAULT_WAIT_MS, retries: int = 4) -> None:
        self.wait_ms = wait_ms
        self.retries = retries
        self._playwright_cm = None
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self.captured_assets: dict[str, dict] = {}

    def __enter__(self) -> "BrowserRenderer":
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Install Playwright and its Chromium browser to render pages: "
                "pip install playwright && playwright install chromium"
            ) from exc

        self._playwright_cm = sync_playwright()
        self._playwright = self._playwright_cm.__enter__()
        self._browser = launch_chromium(self._playwright)
        self._page = self._new_page()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._browser:
            self._browser.close()
        if self._playwright_cm:
            self._playwright_cm.__exit__(exc_type, exc, tb)

    def fetch(self, url: str) -> PageResult:
        if self._page is None:
            raise RuntimeError("BrowserRenderer must be used as a context manager")

        last_result: PageResult | None = None
        for attempt in range(1, self.retries + 1):
            if attempt > 1:
                print(f"[INFO] Browser retry {attempt}/{self.retries}: {url}", flush=True)
                self._page.close()
                self._page = self._new_page()
                self._page.wait_for_timeout(2500 * attempt)

            try:
                result = self._render_once(url)
            except Exception as exc:
                print(f"[WARN] Browser render attempt failed for {url}: {exc}", flush=True)
                continue
            last_result = result
            if not is_probably_blocked(result.html):
                self._sync_browser_cookies()
                return result

        assert last_result is not None
        return last_result

    def _new_page(self):
        page = self._browser.new_page()
        page.on("response", self._capture_response)
        return page

    def _capture_response(self, response) -> None:
        try:
            asset_url = clean_url(response.url)
            if asset_url in self.captured_assets or response.status >= 400:
                return
            content_type = response.headers.get("content-type", "")
            if not is_captureable_response(asset_url, content_type):
                return
            body = response.body()
            if not body:
                return
            path = asset_path_for_url(asset_url)
            write_asset_bytes(asset_url, path, body)
            self.captured_assets[asset_url] = {
                "url": asset_url,
                "local_path": str(path.as_posix()),
                "content_type": content_type or mimetypes.guess_type(path)[0] or "",
                "bytes": len(body),
                "captured_by": "browser",
            }
        except Exception:
            return

    def _render_once(self, url: str) -> PageResult:
        print(f"[INFO] Browser rendering: {url}", flush=True)
        try:
            self._page.goto(url, wait_until="networkidle", timeout=90_000)
        except Exception:
            self._page.goto(url, wait_until="domcontentloaded", timeout=90_000)
        self._page.wait_for_timeout(self.wait_ms)
        for _ in range(6):
            if not is_probably_blocked(self._page.content()):
                break
            self._page.wait_for_timeout(3000)
        try:
            self._page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass
        return PageResult(url=self._page.url, html=self._page.content(), title=self._page.title())

    def _sync_browser_cookies(self) -> None:
        if self._page is None:
            return
        for cookie in self._page.context.cookies():
            SESSION.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain"), path=cookie.get("path", "/"))

    def download_binary(self, url: str) -> tuple[bytes, str]:
        if self._page is None:
            raise RuntimeError("BrowserRenderer must be used as a context manager")

        response = self._page.goto(url, wait_until="load", timeout=45_000)
        if response is None:
            raise RuntimeError("No browser response")
        if response.status >= 400:
            raise RuntimeError(f"Browser returned HTTP {response.status}")
        return response.body(), response.headers.get("content-type", "")


def fetch_page(url: str, force_browser: bool = False) -> PageResult:
    if not force_browser:
        try:
            response = request_url(url)
            html = response.text
            if not is_probably_blocked(html):
                soup = BeautifulSoup(html, "html.parser")
                return PageResult(
                    url=clean_url(response.url),
                    html=html,
                    title=(soup.title.string.strip() if soup.title and soup.title.string else ""),
                )
            print("[WARN] Normal request reached a browser verification page; switching to Chromium.")
        except Exception as exc:
            print(f"[WARN] Normal request failed for {url}: {exc}; switching to Chromium.")

    return fetch_rendered_pages([url])[0]


def fetch_page_with_renderer(
    url: str, renderer: BrowserRenderer | None, force_browser: bool = False
) -> PageResult:
    if force_browser:
        if renderer is None:
            return fetch_rendered_pages([url])[0]
        return renderer.fetch(url)

    try:
        response = request_url(url)
        html = response.text
        if not is_probably_blocked(html):
            soup = BeautifulSoup(html, "html.parser")
            return PageResult(
                url=clean_url(response.url),
                html=html,
                title=(soup.title.string.strip() if soup.title and soup.title.string else ""),
            )
        print("[WARN] Normal request reached a browser verification page; switching to Chromium.", flush=True)
    except Exception as exc:
        print(f"[WARN] Normal request failed for {url}: {exc}; switching to Chromium.", flush=True)

    if renderer is None:
        return fetch_rendered_pages([url])[0]
    return renderer.fetch(url)


def collect_sitemap_urls(
    renderer: BrowserRenderer,
    sitemap_url: str,
    max_pages: int,
    max_sitemaps: int = 20,
) -> list[str]:
    pages: list[str] = []
    seen_pages: set[str] = set()
    seen_sitemaps: set[str] = set()
    pending = [clean_url(sitemap_url)]

    while pending and len(seen_sitemaps) < max_sitemaps and len(pages) < max_pages:
        current = pending.pop(0)
        if current in seen_sitemaps:
            continue
        seen_sitemaps.add(current)

        try:
            result = renderer.fetch(current)
        except Exception as exc:
            print(f"[WARN] Failed sitemap {current}: {exc}", flush=True)
            continue

        soup = BeautifulSoup(result.html, "html.parser")
        candidates: list[str] = []
        candidates.extend(loc.get_text(strip=True) for loc in soup.find_all("loc"))
        candidates.extend(tag.get("href", "") for tag in soup.select("a[href]"))

        for candidate in candidates:
            if not candidate:
                continue
            cleaned = clean_url(urljoin(current, candidate))
            if not same_host(cleaned):
                continue
            if cleaned.endswith(".xml"):
                if cleaned not in seen_sitemaps and cleaned not in pending:
                    pending.append(cleaned)
                continue
            if is_static_asset(cleaned):
                continue
            if cleaned not in seen_pages:
                seen_pages.add(cleaned)
                pages.append(cleaned)
                if len(pages) >= max_pages:
                    break

    return pages


def normalize_page_link(value: str | None, current_url: str) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not value or value.startswith(("#", "mailto:", "tel:", "javascript:", "data:", "blob:")):
        return None

    absolute = clean_url(urljoin(current_url, value))
    if not same_host(absolute):
        return None
    if is_static_asset(absolute):
        return None
    return absolute


def normalize_asset_link(value: str | None, current_url: str) -> str | None:
    if not value:
        return None
    value = value.strip().strip("\"'")
    if not value or value.startswith(("data:", "blob:", "mailto:", "tel:", "javascript:")):
        return None

    absolute = clean_url(urljoin(current_url, value))
    if is_static_asset(absolute):
        return absolute
    return None


def split_srcset(value: str) -> list[str]:
    urls: list[str] = []
    for candidate in value.split(","):
        part = candidate.strip().split()
        if part:
            urls.append(part[0])
    return urls


def collect_from_style(style_value: str, current_url: str) -> set[str]:
    assets: set[str] = set()
    for match in re.finditer(r"url\((?P<url>[^)]+)\)", style_value or "", flags=re.IGNORECASE):
        asset = normalize_asset_link(match.group("url"), current_url)
        if asset:
            assets.add(asset)
    return assets


def collect_from_html(html: str, current_url: str) -> tuple[set[str], set[str]]:
    soup = BeautifulSoup(html, "html.parser")
    pages: set[str] = set()
    assets: set[str] = set()

    for tag in soup.select("a[href], area[href]"):
        page = normalize_page_link(tag.get("href"), current_url)
        if page:
            pages.add(page)

    asset_attrs = ("src", "href", "poster", "data-src", "data-bg", "data-lazyload", "data-thumb")
    for tag in soup.select("[src], [href], [poster], [data-src], [data-bg], [data-lazyload], [data-thumb], [style]"):
        for attr in asset_attrs:
            asset = normalize_asset_link(tag.get(attr), current_url)
            if asset:
                assets.add(asset)
        if tag.get("style"):
            assets.update(collect_from_style(tag["style"], current_url))

    for tag in soup.select("[srcset], [data-srcset]"):
        for attr in ("srcset", "data-srcset"):
            for src in split_srcset(tag.get(attr, "")):
                asset = normalize_asset_link(src, current_url)
                if asset:
                    assets.add(asset)

    return pages, assets


def collect_from_text(text: str, current_url: str) -> set[str]:
    assets: set[str] = set()
    patterns = [
        r"""url\((?P<url>[^)]+)\)""",
        r"""["'](?P<url>[^"']+\.(?:avif|css|eot|gif|ico|jpe?g|js|json|map|mp4|otf|pdf|png|svg|ttf|webm|webp|woff2?|xml)(?:\?[^"']*)?)["']""",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            asset = normalize_asset_link(match.group("url"), current_url)
            if asset:
                assets.add(asset)
    return assets


def download_asset(asset_url: str, renderer: BrowserRenderer | None = None) -> dict | None:
    try:
        print(f"[INFO] Downloading asset: {asset_url}", flush=True)
        response = request_url(asset_url)
        content = response.content
        content_type = response.headers.get("content-type") or ""
    except Exception as exc:
        if renderer is None or not same_host(asset_url):
            print(f"[WARN] Failed asset {asset_url}: {exc}")
            return None
        try:
            print(f"[INFO] Browser downloading asset: {asset_url}", flush=True)
            content, content_type = renderer.download_binary(asset_url)
        except Exception as browser_exc:
            print(f"[WARN] Failed asset {asset_url}: {exc}; browser fallback: {browser_exc}")
            return None

    try:
        path = asset_path_for_url(asset_url)
        write_asset_bytes(asset_url, path, content)
        content_type = content_type or mimetypes.guess_type(path)[0] or ""
        return {
            "url": asset_url,
            "local_path": str(path.as_posix()),
            "content_type": content_type,
            "bytes": len(content),
        }
    except Exception as exc:
        print(f"[WARN] Failed asset {asset_url}: {exc}")
        return None


def download_asset_request_only(asset_url: str) -> tuple[str, dict | None]:
    try:
        print(f"[INFO] Downloading asset: {asset_url}", flush=True)
        response = request_url(asset_url, timeout=18)
        content = response.content
        content_type = response.headers.get("content-type") or ""
        if response.headers.get("content-type", "").startswith("text/") and is_probably_blocked(response.text):
            raise RuntimeError("asset request reached browser verification")

        path = asset_path_for_url(asset_url)
        write_asset_bytes(asset_url, path, content)
        content_type = content_type or mimetypes.guess_type(path)[0] or ""
        return asset_url, {
            "url": asset_url,
            "local_path": str(path.as_posix()),
            "content_type": content_type,
            "bytes": len(content),
        }
    except Exception as exc:
        print(f"[WARN] Failed asset {asset_url}: {exc}", flush=True)
        return asset_url, None


def rewrite_css_urls(path: Path, source_url: str, asset_map: dict[str, Path]) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")

    def replace_url(match: re.Match) -> str:
        raw = match.group("url").strip().strip("\"'")
        asset = normalize_asset_link(raw, source_url)
        if not asset or asset not in asset_map:
            return match.group(0)
        return f"url('{safe_relative_url(path, asset_map[asset])}')"

    rewritten = re.sub(r"url\((?P<url>[^)]+)\)", replace_url, text, flags=re.IGNORECASE)
    if rewritten != text:
        path.write_text(rewritten, encoding="utf-8")


def rewrite_known_asset_urls(text: str, from_path: Path, asset_map: dict[str, Path]) -> str:
    def replace_match(match: re.Match) -> str:
        raw = match.group(0)
        unescaped = raw.replace("\\/", "/")
        asset = clean_url(unescaped)
        if asset not in asset_map:
            return raw
        local = safe_relative_url(from_path, asset_map[asset])
        return local.replace("/", "\\/") if "\\/" in raw else local

    rewritten = TEXT_ASSET_URL_RE.sub(replace_match, text)

    def replace_root_relative(match: re.Match) -> str:
        quote_char = match.group("quote")
        path = match.group("path")
        asset = clean_url("/" + path.replace("\\/", "/"))
        if asset not in asset_map:
            return match.group(0)
        # Root-relative strings inside JS are resolved by the browser relative to
        # the document URL, not relative to this JS file.
        local = site_root_relative_url(asset_map[asset])
        return f"{quote_char}{local}{quote_char}"

    rewritten = ROOT_RELATIVE_ASSET_URL_RE.sub(replace_root_relative, rewritten)

    for base_url in COMMON_ASSET_BASES:
        local_dir = safe_relative_url(from_path, asset_dir_path_for_url(base_url)).rstrip("/") + "/"
        rewritten = rewritten.replace(base_url, local_dir)
        rewritten = rewritten.replace(base_url.replace("/", "\\/"), local_dir.replace("/", "\\/"))

    return rewritten


def rewrite_text_asset_urls(path: Path, asset_map: dict[str, Path]) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rewritten = rewrite_known_asset_urls(text, path, asset_map)
    rewritten = rewrite_site_phone_numbers(rewritten)
    if rewritten != text:
        path.write_text(rewritten, encoding="utf-8")


def rewrite_site_phone_numbers(text: str) -> str:
    """Replace Heritage Mabati's published contact number in the local export."""
    replacements = {
        "+254746667456": "+254" + LOCAL_PHONE_COMPACT[1:],
        "254746667456": "254" + LOCAL_PHONE_COMPACT[1:],
        "+254 746 667 456": "+254 " + LOCAL_PHONE_DISPLAY[1:],
        "254 746 667 456": "254 " + LOCAL_PHONE_DISPLAY[1:],
        "+254-746-667-456": "+254-" + LOCAL_PHONE_DISPLAY[1:].replace(" ", "-"),
        "0746667456": LOCAL_PHONE_COMPACT,
        "0746 667 456": LOCAL_PHONE_DISPLAY,
        "0746-667-456": LOCAL_PHONE_DISPLAY.replace(" ", "-"),
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def local_link_for(url: str, from_path: Path, page_map: dict[str, Path], asset_map: dict[str, Path]) -> str | None:
    cleaned = clean_url(url)
    if cleaned in page_map:
        return safe_relative_url(from_path, page_map[cleaned])
    if cleaned in asset_map:
        return safe_relative_url(from_path, asset_map[cleaned])
    return None


def rewrite_html(html: str, page_url: str, output_path: Path, page_map: dict[str, Path], asset_map: dict[str, Path]) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.select("script[src*='analytics'], script[src*='googletagmanager'], script[src*='google-analytics']"):
        tag.decompose()

    for tag in soup.select("script[id*='wp-emoji'], script[src*='wp-emoji-release']"):
        tag.decompose()

    asset_attrs = ("href", "src", "poster", "data-src", "data-bg", "data-lazyload", "data-thumb")
    for tag in soup.select("[href], [src], [poster], [data-src], [data-bg], [data-lazyload], [data-thumb]"):
        for attr in asset_attrs:
            value = tag.get(attr)
            if not value:
                continue
            absolute = clean_url(urljoin(page_url, value))
            local = local_link_for(absolute, output_path, page_map, asset_map)
            # Shopify emits per-request CSS subset URLs; the browser capture also
            # saves the compiled stylesheet at its query-free alias path.
            parsed_asset = urlparse(absolute)
            if (
                local is None
                and tag.name == "link"
                and "stylesheet" in (tag.get("rel") or [])
                and parsed_asset.netloc.lower() == urlparse(BASE_URL).netloc.lower()
                and parsed_asset.path.endswith("/compiled_assets/styles.css")
            ):
                alias = asset_alias_path_for_url(absolute)
                if alias and alias.exists():
                    local = safe_relative_url(output_path, alias)
            if local:
                tag[attr] = local

    for tag in soup.select("[srcset], [data-srcset]"):
        for attr in ("srcset", "data-srcset"):
            value = tag.get(attr)
            if not value:
                continue
            rewritten_candidates: list[str] = []
            for candidate in value.split(","):
                pieces = candidate.strip().split()
                if not pieces:
                    continue
                absolute = clean_url(urljoin(page_url, pieces[0]))
                local = local_link_for(absolute, output_path, page_map, asset_map)
                pieces[0] = local or pieces[0]
                rewritten_candidates.append(" ".join(pieces))
            tag[attr] = ", ".join(rewritten_candidates)

    for tag in soup.select("[style]"):
        style_value = tag.get("style", "")

        def replace_style_url(match: re.Match) -> str:
            raw = match.group("url").strip().strip("\"'")
            absolute = clean_url(urljoin(page_url, raw))
            local = local_link_for(absolute, output_path, page_map, asset_map)
            return f"url('{local}')" if local else match.group(0)

        tag["style"] = re.sub(r"url\((?P<url>[^)]+)\)", replace_style_url, style_value, flags=re.IGNORECASE)

    for tag in soup.select("script:not([src]), style"):
        if not tag.string:
            continue
        rewritten = rewrite_known_asset_urls(str(tag.string), output_path, asset_map)
        if rewritten != tag.string:
            tag.string.replace_with(rewritten)

    return rewrite_site_phone_numbers(str(soup))


def crawl_site(
    start_url: str,
    max_pages: int,
    force_browser: bool,
    renderer: BrowserRenderer,
    seed_urls: list[str] | None = None,
) -> tuple[dict[str, PageResult], set[str]]:
    pages: dict[str, PageResult] = {}
    assets: set[str] = set()
    pending = [clean_url(url) for url in (seed_urls or [start_url])]
    if clean_url(start_url) not in pending:
        pending.insert(0, clean_url(start_url))

    while pending and len(pages) < max_pages:
        url = pending.pop(0)
        if url in pages:
            continue

        page = fetch_page_with_renderer(url, renderer, force_browser=force_browser)
        cleaned_url = clean_url(page.url)
        if is_probably_blocked(page.html):
            raise RuntimeError(f"Blocked by browser verification page at {cleaned_url}")

        pages[cleaned_url] = page
        found_pages, found_assets = collect_from_html(page.html, cleaned_url)
        assets.update(found_assets)

        for found in sorted(found_pages):
            if found not in pages and found not in pending and len(pending) + len(pages) < max_pages:
                pending.append(found)

        time.sleep(0.05)

    return pages, assets


def download_assets(
    initial_assets: set[str],
    renderer: BrowserRenderer | None = None,
    max_assets: int = 0,
    workers: int = DEFAULT_ASSET_WORKERS,
) -> tuple[dict[str, Path], list[dict]]:
    asset_map: dict[str, Path] = {}
    manifest_assets: list[dict] = []
    pending = list(sorted(initial_assets))

    while pending:
        remaining = max_assets - len(manifest_assets) if max_assets else len(pending)
        if max_assets and remaining <= 0:
            print(f"[WARN] Asset cap reached ({max_assets}); rerun with --max-assets 0 for everything.")
            break

        batch_size = min(max(workers, 1) * 2, len(pending), remaining)
        batch: list[str] = []
        while pending and len(batch) < batch_size:
            asset_url = pending.pop(0)
            if asset_url not in asset_map and asset_url not in batch:
                batch.append(asset_url)

        if not batch:
            continue

        downloaded: list[tuple[str, dict | None]] = []
        if workers > 1:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_map = {executor.submit(download_asset_request_only, asset_url): asset_url for asset_url in batch}
                for future in as_completed(future_map):
                    downloaded.append(future.result())
        else:
            downloaded = [(asset_url, download_asset(asset_url, renderer=renderer)) for asset_url in batch]

        for asset_url, item in downloaded:
            if not item or asset_url in asset_map:
                continue
            path = Path(item["local_path"])
            asset_map[asset_url] = path
            manifest_assets.append(item)

            if path.suffix.lower() in TEXT_EXTENSIONS:
                text = path.read_text(encoding="utf-8", errors="ignore")
                for nested in sorted(collect_from_text(text, asset_url)):
                    if nested not in asset_map and nested not in pending:
                        pending.append(nested)

        time.sleep(0.02)

    return asset_map, manifest_assets


def write_server_helper() -> None:
    helper = """import os
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
"""
    write_text(OUTPUT_DIR / "serve.py", helper)


def write_deploy_files() -> None:
    vercel_config = {
        "cleanUrls": True,
        "trailingSlash": False,
        "headers": [
            {
                "source": "/assets/(.*)",
                "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}],
            }
        ],
        "rewrites": [{"source": "/(.*)", "destination": "/index.html"}],
    }
    write_text(OUTPUT_DIR / "vercel.json", json.dumps(vercel_config, indent=2))
    write_text(OUTPUT_DIR / "_redirects", "/* /index.html 200\n")
    write_text(
        OUTPUT_DIR / "README.md",
        """# Heritage Mabati Static Export

This folder is generated by `kentank.py`.

## Local preview

```bash
python serve.py
```

Then open `http://127.0.0.1:8080`.

Only use this export when you have permission to mirror the source site and its assets.
""",
    )


def save_manifest(source_url: str, pages: dict[str, PageResult], assets: list[dict]) -> None:
    manifest = {
        "source": source_url,
        "export_dir": str(OUTPUT_DIR.as_posix()),
        "page_count": len(pages),
        "asset_count": len(assets),
        "pages": sorted(pages.keys()),
        "assets": assets,
    }
    write_text(MANIFEST_PATH, json.dumps(manifest, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render and export the Heritage Mabati public website.")
    parser.add_argument("--url", default=BASE_URL, help="Website URL to export.")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES, help="Maximum same-host HTML pages to crawl.")
    parser.add_argument("--keep", action="store_true", help="Do not delete the current export folder before running.")
    parser.add_argument("--browser", action="store_true", help="Use Chromium/Playwright rendering for every page.")
    parser.add_argument("--sitemap", action="store_true", help="Seed the crawl from the site's sitemap.xml.")
    parser.add_argument("--wait-ms", type=int, default=DEFAULT_WAIT_MS, help="Milliseconds to wait after browser rendering.")
    parser.add_argument(
        "--asset-workers",
        type=int,
        default=DEFAULT_ASSET_WORKERS,
        help="Parallel asset download workers. Use 1 to disable parallel downloads.",
    )
    parser.add_argument(
        "--download-missing-assets",
        action="store_true",
        help="After browser capture, also try direct requests for assets the browser did not capture.",
    )
    parser.add_argument(
        "--max-assets",
        type=int,
        default=0,
        help="Maximum assets to download. Use 0 for no limit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    global BASE_URL
    BASE_URL = clean_url(args.url)

    ensure_dirs(clean=not args.keep)

    print(f"[INFO] Exporting site: {BASE_URL}")
    with BrowserRenderer(wait_ms=args.wait_ms) as renderer:
        seed_urls = None
        if args.sitemap:
            sitemap_url = urljoin(BASE_URL, "sitemap.xml")
            print(f"[INFO] Reading sitemap: {sitemap_url}", flush=True)
            seed_urls = collect_sitemap_urls(renderer, sitemap_url, args.max_pages)
            print(f"[INFO] Sitemap seed pages: {len(seed_urls)}", flush=True)

        pages, discovered_assets = crawl_site(
            BASE_URL,
            args.max_pages,
            force_browser=args.browser,
            renderer=renderer,
            seed_urls=seed_urls,
        )

        manifest_assets = list(renderer.captured_assets.values())
        asset_map = {url: Path(item["local_path"]) for url, item in renderer.captured_assets.items()}
        missing_assets = discovered_assets.difference(asset_map)

        print(f"[INFO] Browser-captured assets: {len(asset_map)}", flush=True)
        if args.download_missing_assets or not asset_map:
            print(f"[INFO] Downloading {len(missing_assets)} missing discovered assets...", flush=True)
            downloaded_map, downloaded_assets = download_assets(
                missing_assets,
                renderer=renderer,
                max_assets=args.max_assets,
                workers=max(args.asset_workers, 1),
            )
            asset_map.update(downloaded_map)
            manifest_assets.extend(downloaded_assets)
        elif missing_assets:
            print(
                f"[INFO] Skipping {len(missing_assets)} uncaptured assets; use --download-missing-assets to try them.",
                flush=True,
            )

    page_map = {url: page_path_for_url(url) for url in pages}
    for asset_url, path in list(asset_map.items()):
        if path.suffix.lower() == ".css":
            rewrite_css_urls(path, asset_url, asset_map)
        if path.suffix.lower() in {".css", ".js", ".json", ".map", ".svg", ".xml"}:
            rewrite_text_asset_urls(path, asset_map)

    for url, page in pages.items():
        output_path = page_map[url]
        html = rewrite_html(page.html, url, output_path, page_map, asset_map)
        write_text(output_path, html)

    customize_export()

    if (OUTPUT_DIR / "index.html").exists():
        write_text(OUTPUT_DIR / "404.html", (OUTPUT_DIR / "index.html").read_text(encoding="utf-8"))

    write_server_helper()
    write_deploy_files()
    save_manifest(BASE_URL, pages, manifest_assets)

    print(f"[DONE] Static export: {OUTPUT_DIR / 'index.html'}")
    print(f"[DONE] Pages saved:   {len(pages)}")
    print(f"[DONE] Assets saved:  {len(manifest_assets)}")
    print(f"[TIP] Run: python3 {OUTPUT_DIR / 'serve.py'}")


if __name__ == "__main__":
    main()
