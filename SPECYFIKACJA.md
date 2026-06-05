# 34-0: Draft Ekstraklasy — Specyfikacja (GDD)

Gra fanowska, niekomercyjna, inspirowana [38-0.app](https://38-0.app).
Stack: czysty HTML/CSS/JS w jednym pliku `index.html`. Hosting: GitHub Pages. Koszt: 0 zł.

---

## 1. Pętla rozgrywki (core loop)

Jeden „run" trwa ~2–3 min:

1. **Konfiguracja** — gracz wybiera: formację, poziom trudności (rerolle),
   tryb draftu i sposób oceniania zawodników.
2. **Draft (11 rund)** — buduje jedenastkę pozycja po pozycji (patrz §3).
3. **Finał** — wynik składu trafia na ranking. *(Opcja: symulacja sezonu — patrz §6).*

---

## 2. Ekrany

| Ekran | Zawartość |
|---|---|
| Konfiguracja | Formacja (5), Trudność (3), Tryb draftu (2), Oceny (2), „Rozpocznij draft" |
| Draft | Lewa: boisko + formacja + licznik rerolli + pasek postępu. Prawa: koło / lista zawodników |
| Finał | Boisko z jedenastką, OVR, zapis na ranking, kopiowanie składu, ranking lokalny |

---

## 3. Mechanika draftu (jak w 38-0)

11 rund = 11 slotów formacji (np. 4-3-3: GK, LB, CB, CB, RB, CM, CM, CM, LW, ST, RW).

### Tryby draftu
- **Najpierw skład (Squad First)** — zakręć kołem → wylosowany **klub × sezon** →
  lista WSZYSTKICH zawodników tej drużyny → wybierz jednego → przypisz do pasującego, wolnego slotu.
- **Najpierw pozycja (Position First)** — wybierz wolny slot → zakręć o klub →
  wybierz zawodnika pasującego na tę pozycję.

### Rerolle (zależne od trudności)
- Łatwy: 3 · Normalny: 1 · Trudny: 0
- Reroll = ponowne kręcenie kołem. Jeśli wylosowana drużyna nie ma nikogo
  pasującego do wolnych slotów → **darmowe** ponowne kręcenie (anty-blokada).

### Oceny zawodników
- **Sezonowe** — ocena z danego sezonu danego klubu.
- **Prime** — życiowa forma zawodnika (pole `pr`).

---

## 4. Struktura bazy danych (JSON w pliku)

```js
{ club:"Lech Poznań", season:"2009/10", color:"#1f6fd6", players:[
  { n:"Robert Lewandowski", nt:"Polska", r:82, pr:92, p:["ST"] },
  ...
]}
```

- `n` nazwisko · `nt` narodowość · `r` ocena sezonowa (40–99) ·
  `pr` ocena prime (opcjonalnie) · `p` pozycje (tablica kodów).
- **Kody pozycji:** `GK RB LB CB CDM CM CAM RM LM RW LW ST`
  (grupy: BR / OBR / POM / NAP — dla kolorów i symulacji).

### ⚠️ Różnica wobec spec „3 zawodników"
Nasza mechanika wymaga **PEŁNYCH składów** (po ~14–18 zawodników na erę,
pokrywających wszystkie pozycje: min. 1 GK, LB, RB, kilku CB, skrzydła, pomoc, napastnicy) —
bo draftuje się całą jedenastkę z wylosowanej drużyny, a nie 1 z 3 napastników.

### Docelowe rozmiary
| | Teraz | Cel v1 |
|---|---|---|
| Kluby × sezony (karty na kole) | 11 | **24–30** |
| Zawodników na erę | ~14 | 14–18 |
| Łącznie zawodników | 160 | **~400–480** |

---

## 5. Źródła danych
- **[90minut.pl](http://www.90minut.pl)** — składy i sezony (pełne archiwum). Podstawa rosterów.
- **FIFA 09–12** — miały licencję Ekstraklasy → realne oceny dla ery ~2008–2012.
- **Starsze ery (90., złota era Górnika, Wisła 04/05)** — brak w FIFA → oceny szacowane
  z reputacji/statystyk (spójna skala). Oceny traktujemy jako dane referencyjne;
  NIE używamy herbów/grafik z gier.

### ⭐ Ujednolicona skala ocen (jedna miara dla WSZYSTKICH epok)

Cel: `78` znaczy to samo w 1993 i w 2023 — kotwicą jest **klasa i rola zawodnika**, nie rok.

| OVR | Klasa (ta sama w każdej epoce) | Przykłady |
|---|---|---|
| 88–92 | Legenda światowa / czołowy reprezentant | Lewandowski (prime), Lubański (prime) |
| 82–87 | Gwiazda ligi, kluczowy reprezentant | Żurawski, Citko, Radović (prime) |
| 77–81 | Bardzo dobry ligowiec, filar mistrza | Štilić, Ivi López, Mila |
| 72–76 | Solidny pierwszoligowiec | trzon składów mistrzowskich |
| 66–71 | Rotacyjny / młody talent / weteran | rezerwowi, juniorzy |

**Metodyka (obowiązuje całą bazę):**
1. **Era 2009–2012** → kotwiczymy w realnych ocenach FIFA 09–12 (jedyne lata z licencją Ekstraklasy).
2. **Pozostałe ery** → ta sama skala wg: pozycji w reprezentacji, transferów zagranicznych, tytułów/statystyk z 90minut.
3. **Spójność pionowa** — każdy mistrz ma podobny rozkład: ~1 gwiazda 80+, kilku po 75, reszta 72–74,
   żeby składy z różnych dekad były porównywalne na kole i w wyniku.

---

## 6. (Opcja) Symulacja sezonu „34-0" — rozszerzenie ponad 38-0

Zamiast kończyć na liczbie OVR, po drafcie symulujemy **34 kolejki**:

1. Liczymy siłę składu: średni OVR + **bonus/kara za balans pozycji**
   (np. brak prawdziwego bramkarza albo same ataki = kara do obrony).
2. Z siły wyliczamy szanse na mecz, np. OVR 88 → ~92% W / 6% R / 2% P.
3. Rzucamy „kością" 34 razy → bilans (np. 28-4-2).
4. **Cel: 34-0.** Ranking po liczbie zwycięstw (OVR jako rozstrzygnięcie remisów).

To czyni nazwę „34-0" dosłowną i daje mocniejszy hak na social media,
ale **oddala nas od oryginalnego 38-0** (które takiej symulacji nie ma). Decyzja: do ustalenia.

---

## 7. Roadmapa
- [x] Prototyp pełnej mechaniki draftu (formacje, tryby, oceny, rerolle, ranking lokalny)
- [ ] Urealnienie ocen (FIFA 09–12) + spójna skala dla starszych er
- [ ] Rozbudowa bazy do ~24–30 kart (Pogoń, Lechia, Cracovia, więcej sezonów)
- [ ] Decyzja: symulacja sezonu vs czysty OVR-leaderboard
- [ ] Dopracowanie UI (animacja koła, ekran końcowy, mobile/swipe, haptyka)
- [ ] (Później) tryb kampanii / fabuła
