#!/usr/bin/env python3
"""Tabele sezonowe z 90minut -> data/tables.json (pozycja, mecze, bramki strac.).

Sluzy do oceny OBRONCOW i BRAMKARZY: jakosc defensywy = stracone bramki na mecz
+ miejsce w tabeli (czego gole strzelone nie oddaja)."""
import time, json, re, html, subprocess

# rok startowy -> sciezka tabeli "<poziom>/liga<N>"
LIGA = {
 2025:"1/liga14072",2024:"1/liga13482",2023:"1/liga12904",2022:"1/liga12330",
 2021:"1/liga11753",2020:"1/liga11233",2019:"1/liga10549",2018:"0/liga9937",
 2017:"0/liga9322",2016:"0/liga8694",2015:"0/liga8069",2014:"0/liga7466",
 2013:"0/liga6826",2012:"0/liga6218",2011:"0/liga5617",2010:"0/liga4991",
 2009:"0/liga4389",2008:"0/liga3782",2007:"0/liga3155",2006:"0/liga2525",
 2005:"0/liga1944",2004:"0/liga1329",2003:"0/liga632",2002:"0/liga188",2001:"0/liga56",
}

ROW = re.compile(
 r'<td><b>(\d+)\.</b></td><td align="left">[^<]*<a [^>]*>([^<]+)</a></td>'
 r'<td>(\d+)</td><td><b>\d+</b></td><td>\d+</td><td>\d+</td><td>\d+</td>'
 r'<td>(\d+)-(\d+)</td>')

def fetch(path):
    out = subprocess.run(["curl","-s","--max-time","30","http://www.90minut.pl/liga/%s.html"%path],
                         capture_output=True, timeout=40)
    return out.stdout.decode("iso-8859-2","replace")

def parse(t):
    t = re.sub(r">\s+<", "><", t)      # zwiń białe znaki między tagami
    tab = {}
    for m in ROW.finditer(t):
        pos, club, gp, gf, ga = m.groups()
        tab[html.unescape(club).strip()] = {"pos": int(pos), "gp": int(gp),
                                            "gf": int(gf), "ga": int(ga)}
    return tab

if __name__ == "__main__":
    out = {}
    for year in sorted(LIGA):
        season = "%d/%s" % (year, str(year+1)[2:])
        try:
            tab = parse(fetch(LIGA[year]))
        except Exception as e:
            print("%s: BLAD %s" % (season, e)); tab = {}
        out[season] = tab
        best = min(tab.items(), key=lambda x: x[1]["ga"]/max(1,x[1]["gp"])) if tab else None
        print("%s: %2d druzyn%s" % (season, len(tab),
              ("  (najlepsza obrona: %s %d strac.)" % (best[0], best[1]["ga"]) if best else "")))
        time.sleep(0.8)
    json.dump(out, open("data/tables.json","w"), ensure_ascii=False, indent=1)
    print("Zapisano: data/tables.json")
