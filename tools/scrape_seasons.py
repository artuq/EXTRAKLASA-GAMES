#!/usr/bin/env python3
"""Scrapuje cale ligi Ekstraklasy dla podanych sezonow i DOKLADA do data/raw_all.json.

Tylko runda jesienna (mniej zapytan = mniej throttlingu na 90minut),
z ponawianiem prob i odstepami. Laczy z istniejacym raw_all.json (dedup club+sezon)."""
import sys, time, json, re, html, os
sys.path.insert(0, "tools")
import scrape_90minut as S

# (rok startowy, sciezka tabeli na 90minut: "<poziom>/liga<NNN>")
SEASONS = [
 (2017,"0/liga9322"),(2016,"0/liga8694"),(2015,"0/liga8069"),(2014,"0/liga7466"),
 (2013,"0/liga6826"),(2012,"0/liga6218"),(2011,"0/liga5617"),(2010,"0/liga4991"),
 (2009,"0/liga4389"),(2008,"0/liga3782"),(2007,"0/liga3155"),(2006,"0/liga2525"),
 (2005,"0/liga1944"),(2004,"0/liga1329"),(2003,"0/liga632"),(2002,"0/liga188"),
 (2001,"0/liga56"),
]

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
