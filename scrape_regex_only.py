"""Fast regex-only contact scraper (no LLM, no Playwright) for remaining URLs."""

import csv
import re
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(?:\+33[\s.-]?|0)[1-9](?:[\s.-]?\d{2}){4}")
EMAIL_JUNK = (
    "wixpress", "sentry", "example.com", "domain.com", "monsite.fr",
    "godaddy", "sentry.io", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ContactResearchBot/1.0)"}
FIELDS = ["url", "email", "telephone"]


def fetch_regex_contacts(url: str) -> tuple[set, set]:
    emails, phones = set(), set()
    candidates = [url]
    for path in ("contact", "contact/", "nous-contacter", "mentions-legales"):
        candidates.append(urljoin(url if url.endswith("/") else url + "/", path))
    for candidate in candidates:
        try:
            resp = requests.get(candidate, headers=HEADERS, timeout=10)
        except requests.RequestException:
            continue
        if resp.status_code != 200:
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ")
        for m in EMAIL_RE.findall(text):
            if not any(j in m.lower() for j in EMAIL_JUNK):
                emails.add(m.lower())
        for a in soup.select("a[href^='mailto:']"):
            addr = a["href"].replace("mailto:", "").split("?")[0].strip()
            if addr and not any(j in addr.lower() for j in EMAIL_JUNK):
                emails.add(addr.lower())
        for m in PHONE_RE.findall(text):
            digits = re.sub(r"\D", "", m)
            if len(digits) in (10, 11, 12):
                phones.add(m.strip())
        for a in soup.select("a[href^='tel:']"):
            num = a["href"].replace("tel:", "").strip()
            if num:
                phones.add(num)
    return emails, phones


def main():
    urls_file, out_file = sys.argv[1], sys.argv[2]
    with open(urls_file, encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for url in urls:
            print(f"Scraping {url} ...")
            emails, phones = fetch_regex_contacts(url)
            row = {"url": url, "email": ", ".join(sorted(emails)), "telephone": ", ".join(sorted(phones))}
            w.writerow(row)
            f.flush()
            print(f"  -> {row}")
            time.sleep(1)


if __name__ == "__main__":
    main()
