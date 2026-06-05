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

def rate(p):
    """Estymacja OVR na ujednoliconej skali 66-86."""
    g = p["grp"]; apps = p["apps"]; goals = p["goals"]
    r = 70
    r += min(apps // 45, 7)                       # doświadczenie (do +7)
    if g == "ATT":  r += min(goals // 12, 7)      # napastnik: gole
    elif g == "MID": r += min(goals // 18, 5)     # pomocnik: gole
    elif g == "DEF": r += min(goals // 12, 2)     # obrońca: rzadkie gole = jakość
    return max(66, min(86, r))

def prime(r):
    """Ocena 'życiowej formy' — estymacja: lepsi rosną mocniej. Do doszlifowania ręcznie."""
    return max(r, min(99, round(r + 2 + (r - 70) * 0.3)))

def convert(raw):
    out = []
    for c in raw:
        players = []
        for p in c["players"]:
            players.append({"n": p["n"], "nt": p["nt"], "grp": p["grp"],
                            "apps": p["apps"], "goals": p["goals"], "_r": rate(p)})
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
    db = convert(raw)
    js = "// AUTO-GENEROWANE z 90minut przez tools/build_db.py — nie edytuj ręcznie.\n"
    js += "window.EKSTRAKLASA_SQUADS = " + json.dumps(db, ensure_ascii=False, indent=1) + ";\n"
    open(os.path.join(here, "data/ekstraklasa.js"), "w", encoding="utf-8").write(js)
    tot = sum(len(c["players"]) for c in db)
    print(f"Kart: {len(db)}  zawodników (po przycięciu): {tot}")
    print("Zapisano: data/ekstraklasa.js")
