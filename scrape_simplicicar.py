"""
Scrape all Simplicicar franchise concessions (official network site) for
name, address, manager name, phone, email if present.
"""

import csv
import re
import time

import requests
from bs4 import BeautifulSoup

URLS = [
    "https://www.simplicicar.com/content/11-concession-meximieux",
    "https://www.simplicicar.com/content/100-concession-soissons",
    "https://www.simplicicar.com/content/103-concession-vichy",
    "https://www.simplicicar.com/content/106-concession-cannes",
    "https://www.simplicicar.com/content/109-concession-nice",
    "https://www.simplicicar.com/content/770-concession-pamiers",
    "https://www.simplicicar.com/content/112-concession-troyes",
    "https://www.simplicicar.com/content/115-concession-carcassonne",
    "https://www.simplicicar.com/content/118-concession-narbonne",
    "https://www.simplicicar.com/content/793-concession-rodez",
    "https://www.simplicicar.com/content/121-concession-la-ciotat",
    "https://www.simplicicar.com/content/124-concession-marignane",
    "https://www.simplicicar.com/content/128-concession-salon",
    "https://www.simplicicar.com/content/131-concession-caen",
    "https://www.simplicicar.com/content/134-concession-royan",
    "https://www.simplicicar.com/content/137-concession-brive",
    "https://www.simplicicar.com/content/140-concession-beaune",
    "https://www.simplicicar.com/content/143-concession-dijon",
    "https://www.simplicicar.com/content/146-concession-besancon",
    "https://www.simplicicar.com/content/149-concession-pontarlier",
    "https://www.simplicicar.com/content/152-concession-valence",
    "https://www.simplicicar.com/content/155-concession-evreux",
    "https://www.simplicicar.com/content/158-concession-vernon",
    "https://www.simplicicar.com/content/161-concession-brest",
    "https://www.simplicicar.com/content/164-concession-nimes",
    "https://www.simplicicar.com/content/167-concession-vauvert",
    "https://www.simplicicar.com/content/170-oncession-st-gaudens",
    "https://www.simplicicar.com/content/173-concession-toulouse-nord",
    "https://www.simplicicar.com/content/176-concession-toulouse-sud",
    "https://www.simplicicar.com/content/179-concession-merignac",
    "https://www.simplicicar.com/content/182-concession-montpellier",
    "https://www.simplicicar.com/content/185-concession-rennes",
    "https://www.simplicicar.com/content/188-concession-tours",
    "https://www.simplicicar.com/content/629-concession-nord-isere",
    "https://www.simplicicar.com/content/194-concession-vienne",
    "https://www.simplicicar.com/content/197-concession-veauche",
    "https://www.simplicicar.com/content/615-concession-moto-veauche",
    "https://www.simplicicar.com/content/200-concession-puy-en-velay",
    "https://www.simplicicar.com/content/203-concession-orleans",
    "https://www.simplicicar.com/content/206-concession-angers",
    "https://www.simplicicar.com/content/209-concession-reims",
    "https://www.simplicicar.com/content/212-concession-nancy",
    "https://www.simplicicar.com/content/625-concession-lorient",
    "https://www.simplicicar.com/content/215-concession-vannes",
    "https://www.simplicicar.com/content/218-concession-dunkerque",
    "https://www.simplicicar.com/content/221-concession-lille",
    "https://www.simplicicar.com/content/224-concession-beauvais",
    "https://www.simplicicar.com/content/227-concession-compiegne",
    "https://www.simplicicar.com/content/230-concession-st-maximin",
    "https://www.simplicicar.com/content/234-concession-arras",
    "https://www.simplicicar.com/content/373-concession-saint-omer",
    "https://www.simplicicar.com/content/237-concession-pau",
    "https://www.simplicicar.com/content/240-concession-perpignan",
    "https://www.simplicicar.com/content/243-concession-strasbourg",
    "https://www.simplicicar.com/content/248-concession-colmar",
    "https://www.simplicicar.com/content/251-concession-lyon-nord",
    "https://www.simplicicar.com/content/254-concession-lyon-ouest",
    "https://www.simplicicar.com/content/729-concession-st-priest",
    "https://www.simplicicar.com/content/257-concession-la-fleche",
    "https://www.simplicicar.com/content/264-concession-aix-les-bains",
    "https://www.simplicicar.com/content/267-concession-annecy",
    "https://www.simplicicar.com/content/272-concession-genevois",
    "https://www.simplicicar.com/content/275-concession-paris-15",
    "https://www.simplicicar.com/content/278-concession-paris-17eme",
    "https://www.simplicicar.com/content/777-concession-le-havre",
    "https://www.simplicicar.com/content/284-concession-cardonnay",
    "https://www.simplicicar.com/content/592-concession-fontainebleau",
    "https://www.simplicicar.com/content/290-concession-lagny",
    "https://www.simplicicar.com/content/296-concession-coeur-yvelines",
    "https://www.simplicicar.com/content/725-concession-coignieres",
    "https://www.simplicicar.com/content/299-concession-orgeval-verneuil",
    "https://www.simplicicar.com/content/302-concession-abbeville",
    "https://www.simplicicar.com/content/305-concession-amiens",
    "https://www.simplicicar.com/content/308-concession-frejus",
    "https://www.simplicicar.com/content/311-concession-toulon-est",
    "https://www.simplicicar.com/content/314-concession-toulon-ouest",
    "https://www.simplicicar.com/content/317-concession-avignon",
    "https://www.simplicicar.com/content/323-concession-pertuis",
    "https://www.simplicicar.com/content/329-concession-poitiers",
    "https://www.simplicicar.com/content/332-concession-limoges",
    "https://www.simplicicar.com/content/335-concession-bretigny",
    "https://www.simplicicar.com/content/338-concession-villebon",
    "https://www.simplicicar.com/content/346-concession-vaucresson",
    "https://www.simplicicar.com/content/352-concession-raincy",
    "https://www.simplicicar.com/content/349-concession-livry-gargan",
    "https://www.simplicicar.com/content/355-concession-montreuil",
    "https://www.simplicicar.com/content/358-concession-villepinte",
    "https://www.simplicicar.com/content/361-concession-champigny",
    "https://www.simplicicar.com/content/367-concession-magny",
    "https://www.simplicicar.com/content/370-concession-mery",
    "https://www.simplicicar.com/content/687-concession-osny",
    "https://www.simplicicar.com/content/376-concession-guadeloupe",
    "https://www.simplicicar.com/content/379-concession-reunion",
    "https://www.simplicicar.com/content/786-concession-chalon-sur-saone",
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(?:\+33[\s.-]?|0)[1-9](?:[\s.-]?\d{2}){4}")
ADDRESS_RE = re.compile(r"[^\n,]{3,60},?\s*\d{5}\s+[A-Za-zÀ-ÿ0-9'\- ]{2,40}")
EMAIL_JUNK = ("wixpress", "sentry", "example.com", ".png", ".jpg", ".jpeg", ".gif", ".svg")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ContactResearchBot/1.0)"}

FIELDS = ["ville", "url", "adresse", "gerant", "email", "telephone"]


def scrape_concession(url: str) -> dict:
    slug = url.rsplit("concession", 1)[-1].strip("-")
    row = {"ville": slug, "url": url, "adresse": "", "gerant": "", "email": "", "telephone": ""}
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
    except requests.RequestException as e:
        print(f"  ERROR fetching {url}: {e}")
        return row
    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code} for {url}")
        return row

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text("\n")

    emails = {m.lower() for m in EMAIL_RE.findall(text) if not any(j in m.lower() for j in EMAIL_JUNK)}
    row["email"] = ", ".join(sorted(emails))

    phones = set()
    for m in PHONE_RE.findall(text):
        digits = re.sub(r"\D", "", m)
        if len(digits) in (10, 11, 12) and not digits.startswith("0952952025"):
            phones.add(m.strip())
    row["telephone"] = ", ".join(sorted(phones))

    addr_match = ADDRESS_RE.search(text)
    if addr_match:
        row["adresse"] = addr_match.group(0).strip()

    m = re.search(r"Messieurs?\s+[A-ZÀ-Ÿ][\wÀ-ÿ'\- ]+|Madame\s+[A-ZÀ-Ÿ][\wÀ-ÿ'\- ]+|Monsieur\s+[A-ZÀ-Ÿ][\wÀ-ÿ'\- ]+", text)
    if m:
        row["gerant"] = m.group(0).strip()

    return row


def main():
    with open("simplicicar_contacts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for url in URLS:
            print(f"Scraping {url} ...")
            row = scrape_concession(url)
            writer.writerow(row)
            f.flush()
            print(f"  -> {row}")
            time.sleep(1)


if __name__ == "__main__":
    main()
