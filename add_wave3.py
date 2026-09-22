"""Add wave3 contacts (JVVA network + pure independents) to all_contacts.csv, dedup."""

import csv
import re

KNOWN_SLUGS = {
    "beziers": "https://jevendsvotreauto.com/agence-de-beziers/",
    "montelimar": "https://jevendsvotreauto.com/agence-de-montelimar/",
    "montpellier": "https://jevendsvotreauto.com/agence-de-montpellier/",
    "valence": "https://jevendsvotreauto.com/agence-de-valence/",
    "romans": "https://jevendsvotreauto.com/agence-de-romans/",
    "melun": "https://jevendsvotreauto.com/agence-de-melun/",
    "santeny": "https://jevendsvotreauto.com/agence-de-santeny/",
    "tourville": "https://jevendsvotreauto.com/agence-de-tourville-la-riviere/",
    "bayonne": "https://jevendsvotreauto.com/agence-de-bayonne/",
    "tyrosse": "https://jevendsvotreauto.com/agence-de-tyrosse/",
}

JVVA_EMAILS = """antony@jevendsvotreauto.com appoigny@jevendsvotreauto.com argeles@jevendsvotreauto.com
arles@jevendsvotreauto.com aubagne@jevendsvotreauto.com bastia@jevendsvotreauto.com
bayonne@jevendsvotreauto.com beaune@jevendsvotreauto.com bernay@jevendsvotreauto.com
beziers@jevendsvotreauto.com clermont34@jevendsvotreauto.com colmar@jevendsvotreauto.com
dijon@jevendsvotreauto.com larochelle@jevendsvotreauto.com leneubourg@jevendsvotreauto.com
melun@jevendsvotreauto.com montelimar@jevendsvotreauto.com montpellier@jevendsvotreauto.com
mulhouse@jevendsvotreauto.com romans@jevendsvotreauto.com rozay@jevendsvotreauto.com
saintes@jevendsvotreauto.com saintlaurent@jevendsvotreauto.com sallanches@jevendsvotreauto.com
santeny@jevendsvotreauto.com toulouse@jevendsvotreauto.com tourville@jevendsvotreauto.com
valence@jevendsvotreauto.com""".split()

new_rows = []
for email in JVVA_EMAILS:
    slug = email.split("@")[0]
    url = KNOWN_SLUGS.get(slug, "https://jevendsvotreauto.com/")
    new_rows.append({
        "reseau": "JVVA", "nom_ville": slug.upper(), "adresse": "",
        "email": email, "telephone": "0845216000 (standard national)", "url": url,
    })

# Pure independents (clean rows only, filter hosting-provider junk email)
independents = [
    ("AuvergneCentralAuto", "Clermont-Ferrand", "", "", "04 73 14 20 24, 06 69 15 99 58", "https://www.auvergne-central-auto.fr/depot-vente/"),
    ("LeLoftAuto", "Rennes", "", "contact@leloftauto.fr", "06.70.37.41.86", "https://leloftauto.fr/"),
    ("MRMAuto", "Rennes", "", "contact@mrmauto.fr", "02 23 27 91 38", "https://www.mrmauto.fr/"),
    ("RennesAutomobiles", "Rennes", "", "", "02 23 46 43 93, 02 99 54 26 21", "https://www.rennesautomobiles.com/"),
    ("THAutomobiles", "", "", "", "02 55 99 50 25, 06 74 49 53 27", "https://www.thautomobiles.fr/"),
]
for reseau, ville, adresse, email, tel, url in independents:
    new_rows.append({"reseau": reseau, "nom_ville": ville, "adresse": adresse, "email": email, "telephone": tel, "url": url})

# Load existing, append, dedup
with open("all_contacts.csv", encoding="utf-8") as f:
    existing = list(csv.DictReader(f))

seen = set()
for r in existing:
    key = r["email"].lower() if r["email"] else f'{r["telephone"]}|{r["url"]}'
    seen.add(key)

added = 0
for r in new_rows:
    key = r["email"].lower() if r["email"] else f'{r["telephone"]}|{r["url"]}'
    if key in seen:
        continue
    seen.add(key)
    existing.append(r)
    added += 1

with open("all_contacts.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["reseau", "nom_ville", "adresse", "email", "telephone", "url"])
    w.writeheader()
    w.writerows(existing)

print(f"Added {added} new contacts. Total now: {len(existing)}")
