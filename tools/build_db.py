#!/usr/bin/env python3
"""Konwertuje surowe składy z 90minut (raw_*.json) do bazy gry 34-0.

Wyjście: data/ekstraklasa.js  ->  window.EKSTRAKLASA_SQUADS = [...]
Format karty: {club, season, color, players:[{n, nt, r, p:[kody pozycji]}]}

Oceny (r) to ESTYMACJA na ujednoliconej skali (patrz SPECYFIKACJA.md):
baza wg grupy + bonus za karierowe mecze w Ekstraklasie (doświadczenie)
+ bonus za gole (dla pomocy/ataku). Gwiazdy doszlifujemy ręcznie później.
"""
import json, os

COLORS = {
 "Lech Poznań":"#1f6fd6","Górnik Zabrze":"#1452a8","Jagiellonia Białystok":"#f2b705",
 "Raków Częstochowa":"#b3132a","GKS Katowice":"#e0a500","Legia Warszawa":"#0f7a36",
 "Zagłębie Lubin":"#2e8b57","Wisła Płock":"#2462c0","Pogoń Szczecin":"#6c1b3a",
 "Radomiak Radom":"#0e7a3a","Korona Kielce":"#c8102e","Motor Lublin":"#2e6fc0",
 "Cracovia":"#b51d2a","Widzew Łódź":"#d61f2b","Piast Gliwice":"#2348c4",
 "Lechia Gdańsk":"#1aa05a","Arka Gdynia":"#e0b400","Bruk-Bet Termalica Nieciecza":"#2e8b57",
}
POS = {"GK":["GK"], "DEF":["CB","LB","RB"], "MID":["CDM","CM","CAM","LM","RM"],
       "ATT":["ST","LW","RW"]}
MAX_PER_SQUAD = 24   # przytnij do trzonu, żeby koło/listy były grywalne

BASE_G = {"GK":67, "DEF":67, "MID":67, "ATT":67}

# Ręczne overridey: rozpoznawalne gwiazdy, których heurystyka (gole/defensywa)
# nie wychwytuje — głównie twórczy pomocnicy i skrzydłowi. Wartość = "podłoga"
# oceny (jeśli automat dał mniej, podbijamy do tej liczby). Łatwo rozszerzać.
STAR_FLOOR = {
 "Josué": 82, "Ivi López": 81, "Jesús Imaz": 80, "Kristoffer Velde": 79,
 "Michał Skóraś": 79, "Erik Expósito": 79, "Marc Gual": 78, "Damian Kądzior": 77,
 "Ruben Vinagre": 77, "Fran Tudor": 76, "Giannis Papanikolaou": 76,
 "Marcin Cebula": 77, "John Yeboah": 77, "Antonio Colak": 78, "Carlitos": 78,
}

def rate(p, sgoals, team):
    """OVR w skali 'FC-realnej' (62-84). Baza ligowa + MAŁY modyfikator za
    realne staty z DANEGO sezonu: ligowy król strzelców ~77-78, trzon ~68-70,
    dobry BR/obrońca mistrza ~77-79. Skala 85-92 zostaje dla legend."""
    g = p["grp"]; apps = p["apps"]
    r = BASE_G[g]
    r += min(apps // 90, 3)                             # doświadczenie (mały bonus)
    if g in ("GK", "DEF"):
        if team:
            gapg = team["ga"] / max(1, team["gp"])
            r += max(0, min(8, round((1.55 - gapg) * 11)))     # jakość defensywy
            r += max(0, min(2, round((8 - team["pos"]) / 4)))  # klasa zespołu
    elif g == "ATT":
        r += min(round(sgoals * 0.45), 9)              # ~20 goli -> +9 (król ~77)
    elif g == "MID":
        r += min(round(sgoals * 0.4), 6)               # strzelający pomocnik
        if team and team["pos"] <= 3: r += 1
    return max(62, min(84, r))

def prime(r):
    """Ocena 'życiowej formy' — łagodny bonus; młodsi/słabsi mają więcej miejsca na wzrost."""
    return min(97, r + (4 if r < 76 else 2))

def convert(raw, scorers, tables):
    out = []
    for c in raw:
        sg = scorers.get(c["season"], {})
        team = tables.get(c["season"], {}).get(c["club"])   # tabela drużyny w tym sezonie
        players = []
        for p in c["players"]:
            g = sg.get(p["n"], 0)                      # gole w TYM sezonie (0 jeśli nie strzelał)
            ovr = min(88, max(rate(p, g, team), STAR_FLOOR.get(p["n"], 0)))  # heurystyka + override gwiazd
            players.append({"n": p["n"], "nt": p["nt"], "grp": p["grp"],
                            "apps": p["apps"], "_r": ovr})
        # sortuj wg oceny potem doświadczenia, przytnij, ale zachowaj min. 1 GK
        players.sort(key=lambda x: (x["_r"], x["apps"]), reverse=True)
        keep = players[:MAX_PER_SQUAD]
        if not any(x["grp"] == "GK" for x in keep):
            gk = next((x for x in players if x["grp"] == "GK"), None)
            if gk: keep[-1] = gk
        cards = [{"n": x["n"], "nt": x["nt"], "r": x["_r"], "pr": prime(x["_r"]),
                  "p": POS[x["grp"]]} for x in keep]
        out.append({"club": c["club"], "season": c["season"],
                    "color": COLORS.get(c["club"], "#888888"), "players": cards})
    return out

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = "data/raw_all.json" if os.path.exists(os.path.join(here, "data/raw_all.json")) else "data/raw_2025_26.json"
    raw = json.load(open(os.path.join(here, src), encoding="utf-8"))
    sc_path = os.path.join(here, "data/scorers.json")
    scorers = json.load(open(sc_path, encoding="utf-8")) if os.path.exists(sc_path) else {}
    tb_path = os.path.join(here, "data/tables.json")
    tables = json.load(open(tb_path, encoding="utf-8")) if os.path.exists(tb_path) else {}
    db = convert(raw, scorers, tables)
    js = "// AUTO-GENEROWANE z 90minut przez tools/build_db.py — nie edytuj ręcznie.\n"
    js += "window.EKSTRAKLASA_SQUADS = " + json.dumps(db, ensure_ascii=False, indent=1) + ";\n"
    open(os.path.join(here, "data/ekstraklasa.js"), "w", encoding="utf-8").write(js)
    tot = sum(len(c["players"]) for c in db)
    print(f"Kart: {len(db)}  zawodników (po przycięciu): {tot}")
    print("Zapisano: data/ekstraklasa.js")
