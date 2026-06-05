#!/usr/bin/env python3
"""Scrapuje cale ligi Ekstraklasy dla podanych sezonow i DOKLADA do data/raw_all.json.

Tylko runda jesienna (mniej zapytan = mniej throttlingu na 90minut),
z ponawianiem prob i odstepami. Laczy z istniejacym raw_all.json (dedup club+sezon)."""
import sys, time, json, re, html, os
sys.path.insert(0, "tools")
import scrape_90minut as S

# (rok startowy, sciezka tabeli na 90minut: "<poziom>/liga<NNN>")
SEASONS = [(2021,"1/liga11753"),(2020,"1/liga11233"),(2019,"1/liga10549"),(2018,"0/liga9937")]

def clubs_of(path):
    t = S.fetch(f"http://www.90minut.pl/liga/{path}.html")
    seen = {}
    for m in re.finditer(r'skarb\.php\?id_klub=(\d+)&id_sezon=\d+"[^>]*>([^<]+)</a>', t):
        seen.setdefault(int(m.group(1)), html.unescape(m.group(2)).strip())
    return seen

RAW = "data/raw_all.json"
existing = json.load(open(RAW, encoding="utf-8")) if os.path.exists(RAW) else []
by_key = {(c["club"], c["season"]): c for c in existing}

for year, path in SEASONS:
    try:
        cl = clubs_of(path)
    except Exception as e:
        print(f"# {year}: tabela nieosiagalna ({e})", flush=True); continue
    print(f"# {year}/{str(year+1)[2:]}: {len(cl)} klubow", flush=True)
    for cid, name in cl.items():
        try:
            season, players = S.scrape(cid, year, rounds=(1,))
        except Exception as e:
            print(f"  {name:<28} BLAD {e}", flush=True); continue
        if players:
            by_key[(name, season)] = {"club": name, "id_klub": cid,
                                      "season": season, "players": players}
        print(f"  {name:<28} {season} {len(players):>2}", flush=True)
        time.sleep(1.2)

out = list(by_key.values())
json.dump(out, open(RAW, "w"), ensure_ascii=False, indent=1)
print("RAZEM kart:", len(out), " zawodnikow:", sum(len(c['players']) for c in out), flush=True)
