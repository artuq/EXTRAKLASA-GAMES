#!/usr/bin/env python3
"""Scraper składów Ekstraklasy z 90minut.pl -> JSON dla gry 34-0.

90minut ma czyste składy od sezonu 2001/02. Mapowanie sezonów:
  id_sezon = 59 + 2*(rok_startu - 2001)   (2001/02=59, 2009/10=75, 2018/19=93 ...)
Strona kadry: kadra.php?id_klub=<X>&id_sezon=<Y>&jesien=<1=jesień|0=wiosna>
Dane: nazwisko, kraj, grupa pozycji (BR/OBR/POM/NAP), mecze-gole.
Oceny (OVR) trzeba dołożyć osobno wg skali z SPECYFIKACJA.md.

Użycie:  python3 scrape_90minut.py <id_klub> <sezon_startowy>   np. 169 2009
"""
import sys, re, html, json, urllib.request

GRP = {"bramkarze": "GK", "obrońcy": "DEF", "pomocnicy": "MID", "napastnicy": "ATT"}

def season_id(start_year: int) -> int:
    return 59 + 2 * (start_year - 2001)

def fetch(url: str, tries: int = 3) -> str:
    import time as _t
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(req, timeout=35).read()
            return raw.decode("iso-8859-2", "replace")
        except Exception as e:
            last = e; _t.sleep(1.5 * (i + 1))
    raise last

ROW = re.compile(
    r'<a href="/kariera\.php\?id=\d+"[^>]*title="([^"]+)"[^>]*>.*?'      # 1: nazwisko
    r'<img[^>]*title="([^"]+)"[^>]*>.*?'                                  # 2: kraj
    r'(?:<td[^>]*>[^<]*</td>\s*){0,3}'                                    # data/wzrost/klub (pomijamy)
    r'<td[^>]*>\s*(\d+)\s*-\s*(\d+)\s*</td>',                             # 3,4: mecze-gole (Ekstraklasa)
    re.S)

def parse(htmltxt: str):
    # tnij wszystko po nagłówku tabeli kadry
    i = htmltxt.find("kliknij na nazwisko")
    body = htmltxt[i:] if i >= 0 else htmltxt
    # etykieta sezonu z nagłówka tabeli (sezony 2001+ -> "20YY/YY")
    mseason = re.search(r'>\s*[^<>]+ - (20\d{2}/\d{2})\s*[<(]', htmltxt)
    season = mseason.group(1) if mseason else "?"
    # podziel na sekcje pozycji
    parts = re.split(r'<b>(bramkarze|obrońcy|pomocnicy|napastnicy):', body)
    players = []
    for k in range(1, len(parts), 2):
        grp = GRP[parts[k]]
        chunk = parts[k + 1]
        for m in re.finditer(
                r'<a href="/kariera\.php\?id=\d+"[^>]*title="([^"]+)"[^>]*>[^<]*</a>'
                r'.*?title="([^"]+)"'              # kraj (flaga)
                r'.*?(\d+)\s*-\s*(\d+)\s*</td>',   # mecze-gole
                chunk, re.S):
            name, country, apps, goals = m.groups()
            players.append({
                "n": html.unescape(name).strip(),
                "nt": html.unescape(country).split(" i ")[0].strip(),
                "grp": grp, "apps": int(apps), "goals": int(goals),
            })
    return season, players

def scrape(id_klub: int, start_year: int, rounds=(1, 0)):
    sid = season_id(start_year)
    merged = {}
    season_label = f"{start_year}/{str(start_year+1)[2:]}"
    for jesien in rounds:
        url = f"http://www.90minut.pl/kadra.php?id_klub={id_klub}&id_sezon={sid}&jesien={jesien}"
        try:
            season, players = parse(fetch(url))
            if season != "?":
                season_label = season
        except Exception as e:
            sys.stderr.write(f"  (runda {jesien}: {e})\n"); continue
        for p in players:
            merged.setdefault(p["n"], p)
    return season_label, list(merged.values())

if __name__ == "__main__":
    id_klub, start = int(sys.argv[1]), int(sys.argv[2])
    season, players = scrape(id_klub, start)
    print(json.dumps({"id_klub": id_klub, "season": season,
                      "count": len(players), "players": players},
                     ensure_ascii=False, indent=1))
