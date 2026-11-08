# Generator Zadań E8 – Matematyka (wzorzec i statystyka CKE 2019–2026)

Lokalna aplikacja okienkowa w języku **Python (`PyQt6`)** do generowania arkuszy egzaminacyjnych, sprawdzianów i zestawów treningowych na poziomie **Egzaminu Ósmoklasisty z matematyki** – w autentycznej szacie graficznej i kolorystyce arkuszy **CKE `OMAP-100`** oraz z empirycznym silnikiem prawdopodobieństwa opartym na **12 oficjalnych arkuszach CKE z lat 2019–2026 (240 zadań)**.

---

## Najważniejsze funkcje (v2)

1. **Empiryczna statystyka prawdopodobieństwa CKE (2019–2026) + równa redystrybucja %**
   - Wagi wszystkich 12 działów wyznaczane są bezpośrednio z katalogu **12 pełnych arkuszy CKE (240 zadań)** od kwietnia 2019 do czerwca 2026 (`e8_generator/cke_archive.py`):
     - *Geometria płaska*: **20,0%** (48/240)
     - *Liczby i ułamki*: **16,7%** (40/240)
     - *Geometria przestrzenna (bryły)*: **10,0%** (24/240)
     - *Procenty i proporcje*: **8,3%** (20/240)
     - *Wyrażenia algebraiczne*: **7,5%** (18/240)
     - *Równania i zadania tekstowe*: **7,5%** (18/240)
     - *Statystyka, tabele i diagramy*: **7,1%** (17/240)
     - *Potęgi i notacja wykładnicza*: **5,0%** (12/240)
     - *Prędkość, droga, czas*: **5,0%** (12/240)
     - *Prawdopodobieństwo i kombinatoryka*: **5,0%** (12/240)
     - *Pierwiastki*: **4,6%** (11/240)
     - *Układ współrzędnych*: **3,3%** (8/240)
   - **Równa redystrybucja po wykreśleniu działów**: gdy w ustawieniach odznaczysz dowolne działy o łącznym udziale $R = \sum_{j \notin S} p_j$, ich procent jest **dzielony po równo** pomiędzy wszystkie pozostałe aktywne działy ($|S|$):
     $$p'_i = p_i + \frac{R}{|S|}, \qquad \sum_{i \in S} p'_i = 100\%.$$
   - **Losowanie kwot metodą Madowa (0,00% dryftu)**: systematyczne zaokrąglanie reszt gwarantuje, że w każdym pojedynczym arkuszu liczba zadań działu należy do $\{\lfloor N p'_i \rfloor, \lceil N p'_i \rceil\}$, a wartość oczekiwana w serii arkuszy jest dokładnie równa $p'_i$.
   - **Wzorzec 1:1 wybranej sesji CKE**: możliwość wygenerowania arkusza odwzorowującego układ zadań wybranego egzaminu CKE (np. *CKE Maj 2026*, *CKE Maj 2025*, *CKE Maj 2024* itd.) ze świeżymi, losowymi danymi liczbowymi.

2. **Autentyczna szata wizualna i kolory arkuszy CKE `OMAP-100` (2025/2026)**
   - **Okładka CKE `OMAP-100`**: oliwkowy znak `CKE` (`#D8DF8E`), szałwiowy pasek `WYPEŁNIA UCZEŃ` (`#C5D9A4`) nad kratkami `KOD UCZNIA` i `PESEL`, ramka `O-100` w czerwieni CKE (`#C00000`), centralna ramka z zielonym emblematem **`E8`** (`#7FA64E`), `Instrukcja dla ucznia` z zielonymi wyróżnieniami (`#537A26`) oraz wektorowy kod kreskowy `OMAP-100-XXXX`.
   - **Strony wewnętrzne**: bezramkowe szałwiowo-oliwkowe paski nagłówków `Zadanie X. (0–Y)` (`#C5D9A4`), bliźniacze okienka wyboru `[ A | B ]` oraz `[ C | D ]`, tabele `P / F` oraz `Tak / Nie + ponieważ + 1 / 2 / 3`.
   - **Zadania otwarte (`0–2`, `0–3`)**: łososiowo-czerwona kratka skanera `5 × 5 mm` (`#DA8A82`) w czarnej ramce z narożnymi znacznikami pozycjonującymi, pionowymi ostrzeżeniami na marginesach (*„Zapisy na marginesie poza ramką nie będą oceniane.”*) oraz okienkiem `Odpowiedź:`.
   - **Karta odpowiedzi CKE (OMR)** na końcu arkusza + tabela punktacji zadań otwartych dla nauczyciela/egzaminatora.
   - **Osobny PDF z Kluczem Odpowiedzi i Zasadami Oceniania**: szybki klucz, tabela pokrycia % działów CKE oraz pełne rozwiązania krok po kroku ze schematem punktowania CKE.

3. **84 parametryczne szablony zadań CKE + 13 typów dynamicznych rysunków**
   - Po **7 odrębnych wzorców zadań** w każdym z 12 działów E8 (miliardy wariantów liczbowych bez powtórzeń).
   - Dynamiczne rysunki `260 DPI` w kolorystyce CKE: oś liczbowa, układ współrzędnych z kratką, trójkąty prostokątne i równoramienne, proste równoległe z sieczną, trapezy, romb z przekątnymi, okrąg z cięciwą, siatka graniastosłupa ze strzałkami wymiarowymi, akwarium z wodą, diagramy słupkowe, diagramy kołowe z procentami oraz wykresy drogi od czasu $s(t)$.

4. **Wygodne okno graficzne (`PyQt6`)**
   - Żywe etykiety `%` bezpośrednio na checkboxach wszystkich 12 działów aktualizowane natychmiast po każdym kliknięciu,
   - Wbudowany podgląd wydruku A4 (Arkusz CKE oraz Klucz),
   - Wymiana pojedynczego zadania jednym kliknięciem bez utraty pozostałych zadań,
   - Zakładka **„Statystyka i Archiwum CKE”** z wbudowanym symulatorem Monte Carlo (`1 000 arkuszy`) oraz przeglądarką wszystkich 12 sesji CKE z lat 2019–2026.

---

## Szybkie uruchomienie

### Windows
Kliknij dwukrotnie plik **`uruchom_windows.bat`** (skrypt sam utworzy środowisko `.venv`, zainstaluje biblioteki i otworzy okno programu).

### Linux / macOS
```bash
./uruchom_linux_mac.sh
```

### Ręczne uruchomienie z terminala
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Tryb wsadowy CLI (bez otwierania okna)
```bash
# Pełny arkusz CKE 2026 (20 zadań, 30 pkt) wg statystyki CKE:
python main.py --cli --out zestaw_probny --variant "Wersja A" --seed 2026

# Arkusz wzorowany 1:1 na oficjalnej sesji CKE Maj 2026:
python main.py --cli --out wzor_maj2026 --distribution mirror_session:cke_2026_05 --seed 101
```

---

## Testy automatyczne
```bash
python -m unittest discover -s tests -v
```
