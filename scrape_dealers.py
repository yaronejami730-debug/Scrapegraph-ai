"""
Scrape contact info (nom, email, telephone, adresse) from car dealership /
depot-vente websites using ScrapeGraphAI + local Ollama LLM.

Usage:
    uv run python scrape_dealers.py urls.txt output.csv
    (urls.txt: one URL per line)
"""

import csv
import re
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from scrapegraphai.graphs import SmartScraperGraph

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(?:\+33[\s.-]?|0)[1-9](?:[\s.-]?\d{2}){4}")
EMAIL_JUNK = (
    "wixpress", "sentry", "example.com", "domain.com", "monsite.fr",
    "godaddy", "sentry.io", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ContactResearchBot/1.0)"}


def fetch_regex_contacts(url: str) -> tuple[set, set]:
    """Fallback: fetch raw HTML (homepage + /contact) and regex-scan for emails/phones."""
    emails, phones = set(), set()
    candidates = [url]
    for path in ("contact", "contact/", "nous-contacter", "mentions-legales"):
        candidates.append(urljoin(url if url.endswith("/") else url + "/", path))
    seen_html = []
    for candidate in candidates:
        try:
            resp = requests.get(candidate, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                seen_html.append(resp.text)
        except requests.RequestException:
            continue
    for html in seen_html:
        soup = BeautifulSoup(html, "html.parser")
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

GRAPH_CONFIG = {
    "llm": {
        "model": "ollama/llama3:8b",
        "temperature": 0,
        "format": "json",
        "base_url": "http://localhost:11434",
    },
    "embeddings": {
        "model": "ollama/llama3:8b",
        "base_url": "http://localhost:11434",
    },
    "verbose": False,
    "headless": True,
}

PROMPT = (
    "Extrait les informations de contact de cette entreprise (concession "
    "automobile / depot-vente): nom de l'entreprise, adresse postale, "
    "email(s) de contact, numero(s) de telephone. Retourne uniquement les "
    "informations presentes sur la page, sans inventer de donnees."
)

FIELDS = ["url", "nom", "adresse", "email", "telephone"]


def scrape_one(url: str) -> dict:
    row = {"url": url, "nom": "", "adresse": "", "email": "", "telephone": ""}

    # Primary: regex fallback on raw HTML (fast, reliable for emails/phones)
    emails, phones = fetch_regex_contacts(url)

    # Secondary: LLM extraction (catches name/address, and contacts regex misses)
    try:
        graph = SmartScraperGraph(prompt=PROMPT, source=url, config=GRAPH_CONFIG)
        result = graph.run()
    except Exception as e:
        print(f"  (LLM extraction failed: {e})")
        result = None

    if isinstance(result, dict):
        for key in ("nom", "name", "nom_entreprise", "company"):
            if result.get(key):
                row["nom"] = result[key]
                break
        for key in ("adresse", "address"):
            if result.get(key):
                row["adresse"] = result[key]
                break
        for key in ("email", "emails"):
            v = result.get(key)
            if v:
                for e in (v if isinstance(v, list) else [v]):
                    if isinstance(e, str) and not any(j in e.lower() for j in EMAIL_JUNK):
                        emails.add(e.lower())
                break
        for key in ("telephone", "phone", "telephones", "phones"):
            v = result.get(key)
            if v:
                for p in (v if isinstance(v, list) else [v]):
                    if isinstance(p, str):
                        phones.add(p.strip())
                break

    dedup_phones = {}
    for p in phones:
        digits = re.sub(r"\D", "", p)
        if digits.startswith("33"):
            digits = "0" + digits[2:]
        dedup_phones.setdefault(digits, p)

    row["email"] = ", ".join(sorted(emails))
    row["telephone"] = ", ".join(sorted(dedup_phones.values()))
    return row


def main():
    if len(sys.argv) != 3:
        print("Usage: python scrape_dealers.py urls.txt output.csv")
        sys.exit(1)

    urls_file, out_file = sys.argv[1], sys.argv[2]
    with open(urls_file, encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for url in urls:
            print(f"Scraping {url} ...")
            try:
                row = scrape_one(url)
                writer.writerow(row)
                f.flush()
                print(f"  -> {row}")
            except Exception as e:
                print(f"  ERROR on {url}: {e}")
            time.sleep(2)  # be polite, avoid hammering sites


if __name__ == "__main__":
    main()
