#!/usr/bin/env python3
"""Scraper historycznych skladow z Transfermarkt -> data/raw_legendy.json.

Transfermarkt udostepnia sklady lat 90. (czego 90minut nie ma), ale BEZ wycen
rynkowych dla tej ery. Stad: stad bierzemy SKLAD + pozycje, a oceny dokladamy
osobno wg ujednoliconej skali (tools/build_legendy.py)."""
import sys, time, json, re, html, subprocess

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

# (klub, etykieta sezonu, verein, saison_id)
SQUADS = [
 ("Legia Warszawa",  "1994/95", 255, 1994),
 ("Widzew Łódź",     "1995/96", 88,  1995),
 ("ŁKS Łódź",        "1997/98", 256, 1997),
 ("Wisła Kraków",    "1998/99", 422, 1998),
 ("Polonia Warszawa","1999/00", 2745,1999),
]

# polska pozycja z TM -> (grupa, kody slotow)
POSMAP = [
 ("Bramkarz",            "GK", ["GK"]),
 ("Środkowy obrońca",    "DEF",["CB"]),
 ("Prawy obrońca",       "DEF",["RB"]),
 ("Lewy obrońca",        "DEF",["LB"]),
 ("Obrońca",             "DEF",["CB"]),
 ("Defensywny pomocnik", "MID",["CDM","CM"]),
 ("Środkowy pomocnik",   "MID",["CM","CAM"]),
 ("Ofensywny pomocnik",  "MID",["CAM","CM"]),
 ("Prawe skrzydło",      "MID",["RM","RW"]),
 ("Prawy pomocnik",      "MID",["RM","RW"]),
 ("Lewe skrzydło",       "MID",["LM","LW"]),
 ("Lewy pomocnik",       "MID",["LM","LW"]),
 ("Pomocnik",            "MID",["CM"]),
 ("Cofnięty napastnik",  "ATT",["CAM","ST"]),
 ("Prawy napastnik",     "ATT",["RW","ST"]),
 ("Lewy napastnik",      "ATT",["LW","ST"]),
 ("Środkowy napastnik",  "ATT",["ST"]),
 ("Napastnik",           "ATT",["ST"]),
]

def fetch(url):
    out = subprocess.run(["curl", "-s", "--max-time", "30", "-A", UA, url],
                         capture_output=True, timeout=40)
    return out.stdout.decode("utf-8", "replace")

def mappos(txt):
    for key, grp, codes in POSMAP:
        if key in txt:
            return grp, codes
    return "MID", ["CM"]

def parse(htmltxt):
    blocks = re.split(r'<a href="/[^"]*?/profil/spieler/\d+">', htmltxt)[1:]
    out = []
    for b in blocks:
        mn = re.match(r"\s*([^<]+?)\s*</a>", b)
        if not mn:
            continue
        name = html.unescape(mn.group(1)).strip()
        pos = re.search(r"<td>\s*([^<]*?(?:Bramkarz|bro[ńn]ca|omocnik|apastnik|skrzyd|krzyd[lł]o)[^<]*?)\s*</td>", b)
        nat = re.search(r'title="([^"]+)"[^>]*class="flaggenrahmen"', b)
        grp, codes = mappos(pos.group(1) if pos else "")
        out.append({"n": name, "nt": html.unescape(nat.group(1)) if nat else "?",
                    "grp": grp, "p": codes})
    return out

if __name__ == "__main__":
    res = []
    for club, season, verein, saison in SQUADS:
        url = f"https://www.transfermarkt.pl/x/kader/verein/{verein}/saison_id/{saison}"
        try:
            players = parse(fetch(url))
        except Exception as e:
            print(f"{club} {season}: BLAD {e}", file=sys.stderr); players = []
        res.append({"club": club, "season": season, "players": players})
        print(f"{club:<20} {season}  {len(players)} zaw.")
        time.sleep(1.0)
    json.dump(res, open("data/raw_legendy.json", "w"), ensure_ascii=False, indent=1)
    print("Zapisano: data/raw_legendy.json")
