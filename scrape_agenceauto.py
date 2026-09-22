"""
Scrape all L'Agence Automobiliere branches (official network site, own domain,
no third-party directory / ToS issue) for name, address, email, phone.
"""

import csv
import re
import time

import requests
from bs4 import BeautifulSoup

SLUGS = [
    "aix-en-provence", "ajaccio", "amiens", "angers", "annecy", "annemasse",
    "athis-mons", "barcelona", "belfort", "besancon-valentin", "biarritz-bab",
    "bordeaux-rive-droite", "bourg-en-bresse", "brest", "caen", "cergy-pontoise",
    "chalon-sur-saone", "chalons-en-champagne", "chateauroux", "chessy", "dax",
    "dijon", "dole", "dunkerque", "epinal", "epone", "grenoble",
    "gretz-armainvilliers", "guadeloupe", "hericourt", "la-croix-verte",
    "lannion", "lille-seclin", "limoges", "lisboa", "lons-le-saunier",
    "louhans", "lyon", "lyon-nord", "martinique", "metz", "molsheim",
    "montauban", "montbeliard", "montceau-les-mines", "montpellier-est",
    "mulhouse", "mulhouse-sud", "namur-nord-fernelmont", "nancy",
    "nantes-sud-est", "nevers", "nice", "nimes", "nogent-le-rotrou",
    "palaiseau", "ploermel-1", "pont-audemer", "pont-leveque", "pontarlier",
    "pornic", "quimper", "rennes-nord", "rodez", "saint-brieuc", "saint-louis",
    "saint-quentin", "saint-die-des-vosges", "saint-genis-pouilly",
    "saint-malo", "sant-cugat-del-valles", "selestat", "senlis", "sete",
    "strasbourg-nord", "tignieu-jameyzieu", "toulouse-fontenilles",
    "toulouse-nord", "toulouse-sud-est-labege", "tours", "troyes", "tulle",
    "valenciennes", "vannes", "vernon", "vesoul", "viroflay", "wasquehal",
    "yerville",
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(?:\+33[\s.-]?|0)[1-9](?:[\s.-]?\d{2}){4}")
ADDRESS_RE = re.compile(r"\d{1,4}[^\n,]{0,60},?\s*\d{5}\s+[A-Za-zÀ-ÿ0-9'\- ]{2,40}")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ContactResearchBot/1.0)"}

FIELDS = ["ville", "url", "adresse", "email", "telephone"]


def scrape_agency(slug: str) -> dict:
    url = f"https://agenceauto.com/fr/fr/agences/{slug}"
    row = {"ville": slug, "url": url, "adresse": "", "email": "", "telephone": ""}
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

    emails = {m.lower() for m in EMAIL_RE.findall(text) if "agenceauto.com" in m.lower()}
    if not emails:
        emails = {f"{slug}@agenceauto.com"}
    row["email"] = ", ".join(sorted(emails))

    phones = set()
    for m in PHONE_RE.findall(text):
        digits = re.sub(r"\D", "", m)
        if len(digits) in (10, 11, 12):
            phones.add(m.strip())
    row["telephone"] = ", ".join(sorted(phones))

    addr_match = ADDRESS_RE.search(text)
    if addr_match:
        row["adresse"] = addr_match.group(0).strip()

    return row


def main():
    with open("agenceauto_contacts.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for slug in SLUGS:
            print(f"Scraping {slug} ...")
            row = scrape_agency(slug)
            writer.writerow(row)
            f.flush()
            print(f"  -> {row}")
            time.sleep(1)


if __name__ == "__main__":
    main()
