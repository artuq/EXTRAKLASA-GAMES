#!/usr/bin/env python3
"""raw_legendy.json (Transfermarkt) -> data/legendy90.js (karty legend 90s).

Sklady realne z Transfermarkt. Oceny ESTYMOWANE na ujednoliconej skali
(SPECYFIKACJA.md): gwiazdy z STARS, reszta bazowo wg pozycji. Wartosci
rynkowe z lat 90. nie istnieja, wiec to swiadoma estymacja."""
import json, os

COLOR = {
 "Legia Warszawa":"#0f7a36","Widzew Łódź":"#d61f2b","ŁKS Łódź":"#cf1b2b",
 "Wisła Kraków":"#e11d2a","Polonia Warszawa":"#8a1f2c",
}
BASE = {"GK":72,"DEF":71,"MID":71,"ATT":72}
MAX = 18

# poprawki pisowni (Transfermarkt gubi polskie znaki) — tylko kluczowe nazwiska
FIX = {
 "Maciej Szczesny":"Maciej Szczęsny","Marek Jozwiak":"Marek Jóźwiak",
 "Jerzy Podbrozny":"Jerzy Podbroźny","Marcin Mieciel":"Marcin Mięciel",
 "Radoslaw Michalski":"Radosław Michalski","Igor Koziol":"Igor Kozioł",
 "Miroslaw Szymkowiak":"Mirosław Szymkowiak","Rafal Siadaczka":"Rafał Siadaczka",
 "Tomasz Klos":"Tomasz Kłos","Marek Saganowski":"Marek Saganowski",
 "Miroslaw Trzeciak":"Mirosław Trzeciak","Boguslaw Wyparlo":"Bogusław Wyparło",
 "Rafal Niznik":"Rafał Niźnik","Mauro Sergio da Silva":"Mauro Sérgio",
 "Kazimierz Wegrzyn":"Kazimierz Węgrzyn","Radoslaw Kaluzny":"Radosław Kałużny",
 "Olgierd Moskalewicz":"Olgierd Moskalewicz","Bogdan Zajac":"Bogdan Zając",
 "Marek Zajac":"Marek Zając","Igor Golaszewski":"Igor Gołaszewski",
 "Arkadiusz Bak":"Arkadiusz Bąk","Jacek Dabrowski":"Jacek Dąbrowski",
 "Arkadiusz Kaliszan":"Arkadiusz Kaliszan","Lukasz Skrzynski":"Łukasz Skrzyński",
 "Pawel Nowak":"Paweł Nowak","Andrzej Wozniak":"Andrzej Woźniak",
}
# gwiazdy: nazwisko (TM) -> (r, pr)
STARS = {
 "Wojciech Kowalczyk":(81,84),"Jerzy Podbrozny":(76,78),"Jacek Zieliński":(76,78),
 "Marek Jozwiak":(74,76),"Radoslaw Michalski":(76,78),"Maciej Szczesny":(78,80),
 "Marek Citko":(79,83),"Tomasz Łapiński":(77,79),"Marek Koniarek":(78,80),
 "Miroslaw Szymkowiak":(74,80),
 "Tomasz Klos":(78,81),"Miroslaw Trzeciak":(78,80),"Marek Saganowski":(75,80),
 "Tomasz Wieszczycki":(75,77),"Witold Bendkowski":(74,76),
 "Tomasz Frankowski":(80,83),"Kazimierz Wegrzyn":(76,78),"Radoslaw Kaluzny":(76,78),
 "Krzysztof Bukalski":(74,76),"Olgierd Moskalewicz":(74,77),
 "Emmanuel Olisadebe":(80,83),"Arkadiusz Bak":(75,77),"Igor Golaszewski":(74,76),
 "Tomas Zvirgzdauskas":(73,75),"Bartosz Tarachulski":(72,75),
}

def prime(r): return max(r, min(99, round(r + 2 + (r-70)*0.3)))

def build():
    raw = json.load(open("data/raw_legendy.json", encoding="utf-8"))
    out = []
    for c in raw:
        ps = []
        for p in c["players"]:
            r, pr = STARS.get(p["n"], (BASE[p["grp"]], None))
            ps.append({"n": FIX.get(p["n"], p["n"]), "nt": p["nt"],
                       "r": r, "pr": pr or prime(r), "p": p["p"], "_g": p["grp"]})
        ps.sort(key=lambda x: x["r"], reverse=True)
        keep = ps[:MAX]
        if not any(x["_g"] == "GK" for x in keep):
            gk = next((x for x in ps if x["_g"] == "GK"), None)
            if gk: keep[-1] = gk
        cards = [{"n":x["n"],"nt":x["nt"],"r":x["r"],"pr":x["pr"],"p":x["p"]} for x in keep]
        out.append({"club": c["club"], "season": c["season"],
                    "color": COLOR.get(c["club"], "#888"), "players": cards})
    return out

if __name__ == "__main__":
    db = build()
    js = "// AUTO z Transfermarkt (sklady) + skala (oceny) — tools/build_legendy.py\n"
    js += "window.LEGENDY90_SQUADS = " + json.dumps(db, ensure_ascii=False, indent=1) + ";\n"
    open("data/legendy90.js", "w", encoding="utf-8").write(js)
    print("Kart:", len(db), "| zawodnikow:", sum(len(c["players"]) for c in db))
    for c in db:
        top = sorted(c["players"], key=lambda x:-x["r"])[:3]
        print("  %s %s — top: %s" % (c["club"], c["season"],
              ", ".join("%s %d" % (p["n"], p["r"]) for p in top)))
