"""Merge all scraped CSVs into one consolidated, deduplicated contacts file."""

import csv

OUT_FIELDS = ["reseau", "nom_ville", "adresse", "email", "telephone", "url"]
rows = []


def add(reseau, nom_ville, adresse, email, telephone, url):
    if not email and not telephone:
        return
    rows.append({
        "reseau": reseau, "nom_ville": nom_ville, "adresse": adresse,
        "email": email, "telephone": telephone, "url": url,
    })


# TransakAuto (201, full contact data)
with open("transakauto_contacts.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        add("TransakAuto", r["agence"], f'{r["adresse"]}, {r["code_postal"]} {r["ville"]}',
            r["email"], r["telephone"], r["url"])

# L'Agence Automobiliere (90)
with open("agenceauto_contacts.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        add("AgenceAuto", r["ville"], r["adresse"], r["email"], r["telephone"], r["url"])

# Simplicicar (partial, ~65)
with open("simplicicar_contacts.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        add("Simplicicar", r["ville"], r["adresse"], r["email"], r["telephone"], r["url"])

# Independent dealers wave 1
with open("concessions_depot_vente.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        add("Independant", r.get("nom") or r["url"], r.get("adresse", ""), r["email"], r["telephone"], r["url"])

# Independent dealers wave 2 (regex-only)
with open("wave2_regex.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        add("Independant", r["url"], "", r["email"], r["telephone"], r["url"])

# Dedup by email (fallback to phone+url if no email)
seen = set()
deduped = []
for r in rows:
    key = r["email"].lower() if r["email"] else f'{r["telephone"]}|{r["url"]}'
    if key in seen:
        continue
    seen.add(key)
    deduped.append(r)

with open("all_contacts.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
    w.writeheader()
    for r in deduped:
        w.writerow(r)

by_reseau = {}
for r in deduped:
    by_reseau[r["reseau"]] = by_reseau.get(r["reseau"], 0) + 1

print(f"Total contacts (dedup, email or phone present): {len(deduped)}")
for k, v in sorted(by_reseau.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
