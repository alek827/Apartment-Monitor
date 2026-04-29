#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import sys
from urllib.parse import urljoin

try:
    import cloudscraper
except ImportError:
    cloudscraper = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

BASE_URL = "https://www.chestnut-square.com"
TARGET_PATH = "/floor-plan-results"
TARGET_URL = urljoin(BASE_URL, TARGET_PATH)
DATA_FILE = "seen.json"
DEFAULT_CHAT_ID = 6611505561
KEYWORDS = [
    "bed",
    "bath",
    "rent",
    "sq ft",
    "floor plan",
    "apartment",
    "studio",
    "1br",
    "2br",
    "3br",
]


def create_scraper():
    if cloudscraper is None:
        raise RuntimeError(
            "cloudscraper is required to fetch this page because it is protected by Cloudflare. "
            "Install dependencies with: python3 -m pip install -r requirements.txt"
        )
    return cloudscraper.create_scraper()


def clean_text(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def hash_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def fetch_page(url):
    session = create_scraper()
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def make_soup(html):
    if BeautifulSoup is None:
        raise RuntimeError(
            "beautifulsoup4 is required to parse the page. "
            "Install dependencies with: python3 -m pip install -r requirements.txt"
        )
    return BeautifulSoup(html, "html.parser")


def extract_image_url(element):
    for attr in ("data-src", "data-original", "src", "data-lazy-src", "data-lazy"):
        value = element.get(attr)
        if value and isinstance(value, str):
            value = value.strip()
            if value:
                return urljoin(BASE_URL, value)
    return None


def is_candidate_block(text, image_found):
    content = (text or "").lower()
    if not content:
        return False
    if any(keyword in content for keyword in KEYWORDS):
        return True
    if image_found and len(content) > 20:
        return True
    return False


def extract_listing_blocks(soup):
    if soup is None:
        return []

    candidates = []
    visited = set()
    all_containers = soup.find_all(["article", "section", "div", "li"])

    for container in all_containers:
        text = clean_text(container.get_text(separator=" "))
        if not text:
            continue

        image_tag = container.find("img")
        image_url = extract_image_url(image_tag) if image_tag else None
        if is_candidate_block(text, image_url is not None):
            key = hash_text(text + (image_url or ""))
            if key in visited:
                continue
            visited.add(key)

            title = None
            heading = container.find(["h1", "h2", "h3", "h4", "h5"])
            if heading:
                title = clean_text(heading.get_text())
            if not title:
                title = text[:120]

            candidates.append(
                {
                    "id": key,
                    "title": title,
                    "details": text,
                    "image_url": image_url,
                }
            )

    if not candidates:
        body_text = clean_text(soup.body.get_text(separator=" ") if soup.body else soup.get_text(separator=" "))
        first_img = soup.find("img")
        candidates.append(
            {
                "id": hash_text(body_text),
                "title": "Current listing snapshot",
                "details": body_text[:300],
                "image_url": extract_image_url(first_img) if first_img else None,
            }
        )

    return candidates


def load_seen(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_seen(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_telegram_photo(token, chat_id, caption, photo_url):
    api_url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML",
    }
    session = create_scraper()
    response = session.post(api_url, data=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def send_telegram_message(token, chat_id, text):
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    session = create_scraper()
    response = session.post(api_url, data=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def send_notification(item, token, chat_id, dry_run=False):
    caption = f"New apartment listed:\n{item['title']}"
    if item["image_url"]:
        if dry_run:
            print("DRY RUN: sendPhoto", caption, item["image_url"])
            return None
        return send_telegram_photo(token, chat_id, caption, item["image_url"])

    if dry_run:
        print("DRY RUN: sendMessage", caption)
        return None
    return send_telegram_message(token, chat_id, caption)


def run_monitor(url, storage_path, send_live, dry_run=False, test_mode=False, token=None, chat_id=None):
    html = fetch_page(url)
    soup = make_soup(html)
    items = extract_listing_blocks(soup)
    seen = load_seen(storage_path)
    seen_ids = {item["id"] for item in seen.get("items", [])}

    new_items = [item for item in items if item["id"] not in seen_ids]
    removed_items = [item for item in seen.get("items", []) if item["id"] not in {i["id"] for i in items}]

    report = {
        "site": url,
        "found": len(items),
        "new_count": len(new_items),
        "removed_count": len(removed_items),
        "new_items": new_items,
        "removed_items": removed_items,
    }

    if test_mode:
        if not items:
            print("No listings were detected on the page.")
            return report
        item = items[0]
        print("--- Test payload ---")
        print(json.dumps(item, indent=2, ensure_ascii=False))
        if send_live and token and chat_id:
            send_notification(item, token, chat_id, dry_run=dry_run)
        return report

    for item in new_items:
        print("New listing detected:", item["title"])
        if send_live and token and chat_id:
            send_notification(item, token, chat_id, dry_run=dry_run)

    if removed_items:
        print(f"{len(removed_items)} listing(s) appear to have been removed or taken.")
        if send_live and token and chat_id:
            text = f"Apartment removed or taken: {removed_items[0]['title']}"
            if dry_run:
                print("DRY RUN: sendMessage", text)
            else:
                send_telegram_message(token, chat_id, text)

    save_seen(storage_path, {"items": items, "updated": os.path.getmtime(storage_path) if os.path.exists(storage_path) else None})
    return report


def main():
    parser = argparse.ArgumentParser(description="Monitor a floor plan listing page and notify Telegram when listings change.")
    parser.add_argument("--test", action="store_true", help="Fetch the current page and output the first listing as a test payload.")
    parser.add_argument("--dry-run", action="store_true", help="Do not send Telegram notifications; only print what would be sent.")
    parser.add_argument("--no-send", action="store_true", help="Do not send Telegram notifications even if credentials are available.")
    parser.add_argument("--storage", default=DATA_FILE, help="Path to the JSON file that stores seen listing fingerprints.")
    parser.add_argument("--url", default=TARGET_URL, help="URL to monitor.")
    parser.add_argument("--chat-id", type=int, default=os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_CHAT_ID, help="Telegram chat ID (defaults to env or default ID).")
    args = parser.parse_args()

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    send_live = not args.no_send and bool(token)
    if args.no_send:
        send_live = False

    if send_live and not token:
        print("Error: TELEGRAM_BOT_TOKEN not set but trying to send live notifications.")
        sys.exit(1)

    report = run_monitor(args.url, args.storage, send_live, dry_run=args.dry_run, test_mode=args.test, token=token, chat_id=args.chat_id)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if not args.test and report["new_count"] == 0 and report["removed_count"] == 0:
        print("No changes detected.")


if __name__ == "__main__":
    main()
