#!/usr/bin/env python3
"""Scrapuje całe ligi Ekstraklasy dla kilku sezonów -> data/raw_all.json.

Tylko runda jesienna (mniej zapytań = mniej throttlingu na 90minut),
z ponawianiem prób i odstępami między zapytaniami."""
import sys, time, json, re, html
sys.path.insert(0, "tools")
import scrape_90minut as S

# (rok startowy, numer strony tabeli na 90minut)
SEASONS = [(2025,"liga14072"),(2024,"liga13482"),(2023,"liga12904"),(2022,"liga12330")]

def clubs_of(liga):
    t = S.fetch(f"http://www.90minut.pl/liga/1/{liga}.html")
    seen = {}
    for m in re.finditer(r'skarb\.php\?id_klub=(\d+)&id_sezon=\d+"[^>]*>([^<]+)</a>', t):
        seen.setdefault(int(m.group(1)), html.unescape(m.group(2)).strip())
    return seen

out = []
for year, liga in SEASONS:
    try:
        cl = clubs_of(liga)
    except Exception as e:
        print(f"# {year}: tabela nieosiagalna ({e})", flush=True); continue
    print(f"# {year}/{str(year+1)[2:]}: {len(cl)} klubow", flush=True)
    for cid, name in cl.items():
        try:
            season, players = S.scrape(cid, year, rounds=(1,))
        except Exception as e:
            print(f"  {name:<28} BLAD {e}", flush=True); continue
        if players:
            out.append({"club": name, "id_klub": cid, "season": season, "players": players})
        print(f"  {name:<28} {season} {len(players):>2}", flush=True)
        time.sleep(1.2)

json.dump(out, open("data/raw_all.json", "w"), ensure_ascii=False, indent=1)
print("RAZEM kart:", len(out), " zawodnikow:", sum(len(c['players']) for c in out), flush=True)
