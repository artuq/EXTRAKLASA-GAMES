#!/usr/bin/env python3
"""Gole SEZONOWE z 90minut (strzelcy.php?id=<liga>) -> data/scorers.json.

Naprawia ocenianie: zamiast goli karierowych uzywamy goli z DANEGO sezonu,
zeby krol strzelcow danego roku mial wysoka ocene (a nie weteran z dluga kariera)."""
import time, json, re, html, subprocess

# sezon (rok startowy) -> numer strony ligi na 90minut
LIGA = {
 2025:14072,2024:13482,2023:12904,2022:12330,2021:11753,2020:11233,2019:10549,
 2018:9937,2017:9322,2016:8694,2015:8069,2014:7466,2013:6826,2012:6218,2011:5617,
 2010:4991,2009:4389,2008:3782,2007:3155,2006:2525,2005:1944,2004:1329,2003:632,
 2002:188,2001:56,
}

def fetch(liga):
    out = subprocess.run(["curl","-s","--max-time","30","http://www.90minut.pl/strzelcy.php?id=%d"%liga],
                         capture_output=True, timeout=40)
    return out.stdout.decode("iso-8859-2","replace")

def parse(t):
    # sekcja po naglowku "Strzelcy"
    i = t.find("Strzelcy</u>")
    seg = t[i:i+40000] if i>=0 else t
    goals = {}
    for m in re.finditer(r"<b>\s*(\d+)\s*gol\w*\s*</b>\s*-\s*(.*?)(?=<b>\s*\d+\s*gol|</td>|</table>)", seg, re.S):
        n = int(m.group(1))
        for pm in re.finditer(r"([^(,<>]+?)\s*\(([^)]+)\)", m.group(2)):
            name = html.unescape(pm.group(1)).strip()
            if len(name) > 2:
                goals[name] = max(goals.get(name, 0), n)
    return goals

if __name__ == "__main__":
    out = {}
    for year in sorted(LIGA):
        season = "%d/%s" % (year, str(year+1)[2:])
        try:
            g = parse(fetch(LIGA[year]))
        except Exception as e:
            print("%s: BLAD %s" % (season, e)); g = {}
        out[season] = g
        top = sorted(g.items(), key=lambda x:-x[1])[:1]
        print("%s: %d strzelcow%s" % (season, len(g), ("  (max: %s %d)" % top[0] if top else "")))
        time.sleep(0.8)
    json.dump(out, open("data/scorers.json","w"), ensure_ascii=False, indent=1)
    print("Zapisano: data/scorers.json")
