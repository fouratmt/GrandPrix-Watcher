"""Monitor a blog/category page for newly published matching video posts."""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
import sys
import time
import tomllib
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = "config.toml"
DEFAULT_USER_AGENT = "grandprix-watcher/0.1.0 (+https://fullraces.com/2026 monitor)"
EVENT_REGEXES = {
    "race": r"^RACE\s*-",
    "sprint": r"^Sprint\s*-",
    "qualifying": r"^Qualifying\s*-",
    "practice": r"^(?:\d+(?:st|nd|rd|th)\s+)?Practice\s*-",
    "sprint-qualifying": r"^Sprint Qualifying\s*-",
    "sprint_qualifying": r"^Sprint Qualifying\s*-",
    "sq": r"^Sprint Qualifying\s*-",
    "paddock": r"^Paddock Uncut\s*-",
    "press": r"^Drivers Press Conference\s*-",
    "press-conference": r"^Drivers Press Conference\s*-",
}
GRAND_PRIX_ALIASES = {
    "australia": ["australian grand prix"],
    "australian": ["australian grand prix"],
    "melbourne": ["australian grand prix"],
    "albert park": ["australian grand prix"],
    "china": ["chinese grand prix"],
    "chinese": ["chinese grand prix"],
    "shanghai": ["chinese grand prix"],
    "japan": ["japanese grand prix"],
    "japanese": ["japanese grand prix"],
    "suzuka": ["japanese grand prix"],
    "bahrain": ["bahrain grand prix"],
    "sakhir": ["bahrain grand prix"],
    "saudi": ["saudi arabian grand prix"],
    "saudi arabia": ["saudi arabian grand prix"],
    "saudi arabian": ["saudi arabian grand prix"],
    "arabia": ["saudi arabian grand prix"],
    "jeddah": ["saudi arabian grand prix"],
    "miami": ["miami grand prix"],
    "florida": ["miami grand prix"],
    "canada": ["canadian grand prix", "grand prix du canada"],
    "canadian": ["canadian grand prix", "grand prix du canada"],
    "montreal": ["canadian grand prix", "grand prix du canada"],
    "monaco": ["monaco grand prix", "grand prix de monaco"],
    "monte carlo": ["monaco grand prix", "grand prix de monaco"],
    "barcelona": ["barcelona catalunya grand prix", "grand prix de barcelona catalunya"],
    "barcelona catalunya": ["barcelona catalunya grand prix", "grand prix de barcelona catalunya"],
    "catalunya": ["barcelona catalunya grand prix", "grand prix de barcelona catalunya"],
    "catalonia": ["barcelona catalunya grand prix", "grand prix de barcelona catalunya"],
    "spain": ["spanish grand prix", "gran premio de espana"],
    "spanish": ["spanish grand prix", "gran premio de espana"],
    "madrid": ["spanish grand prix", "gran premio de espana"],
    "austria": ["austrian grand prix"],
    "austrian": ["austrian grand prix"],
    "spielberg": ["austrian grand prix"],
    "great britain": ["british grand prix"],
    "britain": ["british grand prix"],
    "british": ["british grand prix"],
    "uk": ["british grand prix"],
    "united kingdom": ["british grand prix"],
    "england": ["british grand prix"],
    "silverstone": ["british grand prix"],
    "belgium": ["belgian grand prix"],
    "belgian": ["belgian grand prix"],
    "spa": ["belgian grand prix"],
    "spa francorchamps": ["belgian grand prix"],
    "hungary": ["hungarian grand prix"],
    "hungarian": ["hungarian grand prix"],
    "budapest": ["hungarian grand prix"],
    "hungaroring": ["hungarian grand prix"],
    "netherlands": ["dutch grand prix"],
    "dutch": ["dutch grand prix"],
    "holland": ["dutch grand prix"],
    "zandvoort": ["dutch grand prix"],
    "italy": ["italian grand prix", "gran premio d italia"],
    "italian": ["italian grand prix", "gran premio d italia"],
    "monza": ["italian grand prix", "gran premio d italia"],
    "azerbaijan": ["azerbaijan grand prix"],
    "baku": ["azerbaijan grand prix"],
    "singapore": ["singapore grand prix"],
    "usa": ["united states grand prix"],
    "us": ["united states grand prix"],
    "united states": ["united states grand prix"],
    "america": ["united states grand prix"],
    "austin": ["united states grand prix"],
    "cota": ["united states grand prix"],
    "texas": ["united states grand prix"],
    "mexico": ["mexico city grand prix", "mexican grand prix", "gran premio de la ciudad de mexico"],
    "mexican": ["mexico city grand prix", "mexican grand prix", "gran premio de la ciudad de mexico"],
    "mexico city": ["mexico city grand prix", "mexican grand prix", "gran premio de la ciudad de mexico"],
    "brazil": ["sao paulo grand prix", "brazilian grand prix", "grande premio de sao paulo"],
    "brazilian": ["sao paulo grand prix", "brazilian grand prix", "grande premio de sao paulo"],
    "sao paulo": ["sao paulo grand prix", "grande premio de sao paulo"],
    "sao-paulo": ["sao paulo grand prix", "grande premio de sao paulo"],
    "interlagos": ["sao paulo grand prix", "brazilian grand prix", "grande premio de sao paulo"],
    "las vegas": ["las vegas grand prix"],
    "las-vegas": ["las vegas grand prix"],
    "vegas": ["las vegas grand prix"],
    "nevada": ["las vegas grand prix"],
    "qatar": ["qatar grand prix"],
    "lusail": ["qatar grand prix"],
    "doha": ["qatar grand prix"],
    "abu dhabi": ["abu dhabi grand prix"],
    "abu-dhabi": ["abu dhabi grand prix"],
    "uae": ["abu dhabi grand prix"],
    "yas marina": ["abu dhabi grand prix"],
    "yas-marina": ["abu dhabi grand prix"],
}


@dataclass(frozen=True)
class LinkItem:
    title: str
    url: str

    @property
    def key(self) -> str:
        return self.url


@dataclass
class WatchConfig:
    url: str
    match_all: list[str]
    match_any: list[str]
    grand_prix_terms: list[str]
    regex: str
    state_file: Path
    notify_existing: bool
    include_seen: bool
    max_pages: int
    interval_seconds: int
    user_agent: str


@dataclass
class NotifyConfig:
    methods: list[str]
    webhook_url: str


@dataclass
class AppConfig:
    watch: WatchConfig
    notify: NotifyConfig


class LinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self._current_href: str | None = None
        self._text_parts: list[str] = []
        self.links: list[LinkItem] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if not href:
            return
        self._current_href = urllib.parse.urljoin(self.base_url, href)
        self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._current_href:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._current_href:
            return
        title = normalize_text(" ".join(self._text_parts))
        if title:
            self.links.append(LinkItem(title=title, url=self._current_href))
        self._current_href = None
        self._text_parts = []


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_search_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value)
    return normalize_text(value).casefold()


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as config_file:
        return tomllib.load(config_file)


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    raise TypeError(f"Expected string or list of strings, got {type(value).__name__}")


def normalize_grand_prix(value: str) -> list[str]:
    normalized = normalize_search_text(value)
    if normalized in GRAND_PRIX_ALIASES:
        return GRAND_PRIX_ALIASES[normalized]
    if normalized.endswith(" grand prix"):
        return [normalized]
    return [f"{normalized} grand prix"]


def event_regex(value: str) -> str:
    normalized = normalize_search_text(value).replace(" ", "-")
    if normalized not in EVENT_REGEXES:
        supported = ", ".join(
            sorted({"race", "sprint", "qualifying", "practice", "sprint-qualifying", "paddock", "press"})
        )
        raise SystemExit(f"Unknown event: {value}. Supported: {supported}.")
    return EVENT_REGEXES[normalized]


def build_config(args: argparse.Namespace) -> AppConfig:
    raw = load_config(Path(args.config))
    watch_raw = raw.get("watch", {})
    notify_raw = raw.get("notify", {})

    url = args.url or watch_raw.get("url")
    if not url:
        raise SystemExit("Missing page URL. Set [watch].url or pass --url.")

    match_all = args.match_all if args.match_all else as_string_list(watch_raw.get("match_all"))
    grand_prix = args.grand_prix or watch_raw.get("grand_prix")
    grand_prix_terms = normalize_grand_prix(str(grand_prix)) if grand_prix else []
    match_any = args.match_any if args.match_any else as_string_list(watch_raw.get("match_any"))
    event = args.event or watch_raw.get("event")
    if args.regex is not None:
        regex = args.regex
    elif event:
        regex = event_regex(str(event))
    else:
        regex = str(watch_raw.get("regex", ""))
    state_file = Path(args.state_file or watch_raw.get("state_file", ".crawler_state.json"))
    notify_existing = bool(
        args.notify_existing if args.notify_existing else watch_raw.get("notify_existing", False)
    )
    include_seen = bool(args.include_seen if args.include_seen else watch_raw.get("include_seen", False))
    max_pages = int(args.max_pages or watch_raw.get("max_pages", 3))
    interval_seconds = int(args.interval or watch_raw.get("interval_seconds", 900))
    user_agent = str(watch_raw.get("user_agent", DEFAULT_USER_AGENT))

    methods = args.notify if args.notify else as_string_list(notify_raw.get("methods")) or ["console"]
    webhook_url = str(args.webhook_url or notify_raw.get("webhook_url", ""))

    return AppConfig(
        watch=WatchConfig(
            url=str(url),
            match_all=match_all,
            match_any=match_any,
            grand_prix_terms=grand_prix_terms,
            regex=regex,
            state_file=state_file,
            notify_existing=notify_existing,
            include_seen=include_seen,
            max_pages=max_pages,
            interval_seconds=interval_seconds,
            user_agent=user_agent,
        ),
        notify=NotifyConfig(methods=methods, webhook_url=webhook_url),
    )


def fetch_html(url: str, user_agent: str) -> str:
    """Fetch a page and return decoded HTML."""
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} while fetching {url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not fetch {url}: {exc.reason}") from exc


def extract_links(html: str, base_url: str) -> list[LinkItem]:
    """Extract unique links from HTML, resolving relative URLs against base_url."""
    parser = LinkParser(base_url)
    parser.feed(html)

    seen: set[str] = set()
    unique_links: list[LinkItem] = []
    for link in parser.links:
        if link.key in seen:
            continue
        seen.add(link.key)
        unique_links.append(link)
    return unique_links


def is_pagination_link(link: LinkItem, source_url: str) -> bool:
    title = normalize_search_text(link.title)
    is_pagination_title = title.isdigit() or title in {"next", "previous", "prev"}
    if not (is_pagination_title or link.title.strip() in {"»", "«", ">", "<"}):
        return False

    source = urllib.parse.urlparse(source_url)
    target = urllib.parse.urlparse(link.url)
    if target.netloc != source.netloc:
        return False

    return target.path.rstrip("/") != source.path.rstrip("/") or target.query != source.query


def crawl_links(config: WatchConfig) -> list[LinkItem]:
    """Crawl the configured listing URL and pagination links up to max_pages."""
    pages_to_fetch = [config.url]
    fetched_pages: set[str] = set()
    all_links: list[LinkItem] = []
    seen_links: set[str] = set()

    while pages_to_fetch and len(fetched_pages) < max(1, config.max_pages):
        page_url = pages_to_fetch.pop(0)
        if page_url in fetched_pages:  # pragma: no cover
            continue

        html = fetch_html(page_url, config.user_agent)
        fetched_pages.add(page_url)
        links = extract_links(html, page_url)

        for link in links:
            if link.key not in seen_links:
                seen_links.add(link.key)
                all_links.append(link)

            if (
                is_pagination_link(link, page_url)
                and link.url not in fetched_pages
                and link.url not in pages_to_fetch
            ):
                pages_to_fetch.append(link.url)

    return all_links


def item_matches(item: LinkItem, config: WatchConfig) -> bool:
    """Return True when a link satisfies all configured matching rules."""
    haystack = normalize_search_text(f"{item.title} {item.url}")

    if config.match_all and not all(normalize_search_text(term) in haystack for term in config.match_all):
        return False

    if config.match_any and not any(normalize_search_text(term) in haystack for term in config.match_any):
        return False

    if config.grand_prix_terms and not any(
        normalize_search_text(term) in haystack for term in config.grand_prix_terms
    ):
        return False

    return not bool(config.regex and not re.search(config.regex, f"{item.title} {item.url}", re.IGNORECASE))


def load_seen(state_file: Path) -> set[str]:
    if not state_file.exists():
        return set()
    with state_file.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return set(data.get("seen", []))


def save_seen(state_file: Path, seen: set[str]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {"seen": sorted(seen), "updated_at": int(time.time())}
    with state_file.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)
        file.write("\n")


def notify_console(item: LinkItem) -> None:
    print(f"New match: {item.title}\n{item.url}\n")


def notify_macos(item: LinkItem) -> None:
    if platform.system() != "Darwin" or not shutil.which("osascript"):
        print("macOS notifications require AppleScript on macOS.", file=sys.stderr)
        return

    title = "New video match"
    script = (
        "display notification "
        f"{json.dumps(item.title)} with title {json.dumps(title)} "
        f"subtitle {json.dumps(item.url)}"
    )
    subprocess.run(["osascript", "-e", script], check=False)


def notify_desktop(item: LinkItem) -> None:
    system = platform.system()
    if system == "Darwin":
        notify_macos(item)
        return

    if system == "Linux" and shutil.which("notify-send"):
        title = "New video match"
        subprocess.run(["notify-send", title, f"{item.title}\n{item.url}"], check=False)
        return

    print("Desktop notifications are not available on this platform.", file=sys.stderr)


def notify_browser(item: LinkItem) -> None:
    opened = webbrowser.open(item.url, new=2)
    if opened:
        print(f"Opened in browser: {item.url}")
    else:
        print(f"Could not open browser for: {item.url}", file=sys.stderr)


def notify_webhook(item: LinkItem, webhook_url: str) -> None:
    if not webhook_url:
        print("Skipping webhook notification: webhook_url is empty.", file=sys.stderr)
        return

    body = json.dumps({"title": item.title, "url": item.url}).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()


def notify(item: LinkItem, config: NotifyConfig) -> None:
    for method in config.methods:
        method_name = method.strip().casefold()
        if method_name == "console":
            notify_console(item)
        elif method_name == "macos":
            notify_macos(item)
        elif method_name == "desktop":
            notify_desktop(item)
        elif method_name == "browser":
            notify_browser(item)
        elif method_name == "webhook":
            notify_webhook(item, config.webhook_url)
        else:
            print(f"Unknown notification method: {method}", file=sys.stderr)


def check_once(config: AppConfig) -> int:
    """Run one crawler check, notify new matches, update state, and return match count."""
    matches = [item for item in crawl_links(config.watch) if item_matches(item, config.watch)]
    seen = load_seen(config.watch.state_file)

    if config.watch.include_seen:
        for item in matches:
            notify(item, config.notify)
        save_seen(config.watch.state_file, seen | {item.key for item in matches})
        print(
            f"Checked {config.watch.url}: "
            f"visited {len(matches)} match(es), including already seen matches."
        )
        return len(matches)

    if not seen and not config.watch.notify_existing:
        save_seen(config.watch.state_file, {item.key for item in matches})
        print(f"Initialized state with {len(matches)} existing match(es). No notifications sent.")
        return 0

    new_matches = [item for item in matches if item.key not in seen]
    for item in new_matches:
        notify(item, config.notify)
        seen.add(item.key)

    save_seen(config.watch.state_file, seen | {item.key for item in matches})
    print(f"Checked {config.watch.url}: {len(new_matches)} new match(es), {len(matches)} total match(es).")
    return len(new_matches)


def parse_args() -> argparse.Namespace:  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Monitor a page for newly uploaded video posts matching keywords or a regex."
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to TOML config file.")
    parser.add_argument("--url", help="Page URL to monitor. Overrides [watch].url.")
    parser.add_argument(
        "--match",
        dest="match_all",
        action="append",
        help="Keyword that must be present. Can be repeated.",
    )
    parser.add_argument(
        "--any",
        dest="match_any",
        action="append",
        help="Keyword where at least one must be present. Can be repeated.",
    )
    parser.add_argument("--regex", help="Regex that must match the title or URL.")
    parser.add_argument(
        "--grand-prix",
        help="Grand Prix location shorthand. Example: japan matches Japanese Grand Prix.",
    )
    parser.add_argument(
        "--event",
        help="Event shorthand: race, sprint, qualifying, practice, sprint-qualifying, paddock, press.",
    )
    parser.add_argument("--state-file", help="JSON file used to remember seen matches.")
    parser.add_argument("--max-pages", type=int, help="Maximum listing pages to crawl.")
    parser.add_argument(
        "--notify",
        action="append",
        choices=["console", "macos", "desktop", "browser", "webhook"],
        help="Notification method. Can be repeated.",
    )
    parser.add_argument("--webhook-url", help="Webhook URL for --notify webhook.")
    parser.add_argument(
        "--notify-existing",
        action="store_true",
        help="Alert for matches found on first run.",
    )
    parser.add_argument(
        "--include-seen",
        action="store_true",
        help="Notify/open matching links even if they are already in the state file.",
    )
    parser.add_argument("--watch", action="store_true", help="Keep checking forever.")
    parser.add_argument("--interval", type=int, help="Seconds between checks in --watch mode.")
    return parser.parse_args()


def main() -> int:  # pragma: no cover
    args = parse_args()
    config = build_config(args)

    if args.watch:
        while True:
            try:
                check_once(config)
            except Exception as exc:
                print(f"Check failed: {exc}", file=sys.stderr)
            time.sleep(config.watch.interval_seconds)

    return 0 if check_once(config) >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
