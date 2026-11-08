# Generator Zadań E8 – Matematyka (styl i poziom CKE)

Lokalny, okienkowy program w języku **Python (PyQt6)** do generowania arkuszy próbnych oraz zestawów zadań z matematyki na poziomie **Egzaminu Ósmoklasisty (E8)** – wzorowany bezpośrednio na autentycznych arkuszach Centralnej Komisji Egzaminacyjnej (CKE) z lat 2019–2026.

---

## Najważniejsze możliwości programu

- **Wygodny interfejs okienkowy (PyQt6)**:
  - gotowe szablony jednym kliknięciem:
    - **Pełny arkusz CKE 2025/2026** (21 zadań · 30 pkt · 125 min),
    - **Pełny arkusz CKE Maj 2026** (20 zadań · 30 pkt · 125 min),
    - **Arkusz CKE z lat 2021–2024** (19 zadań · 25 pkt · 100 min),
    - **Szybki sprawdzian / kartkówka** (10 zadań · 13 pkt · 45 min),
  - **pełna własna konfiguracja**: wybór konkretnych działów lub całego materiału E8, dowolna liczba zadań zamkniętych (1 pkt), otwartych krótkich (0–2 pkt) i rozszerzonych (0–3 pkt), filtrowanie form zadań zamkniętych (`ABCD`, `Prawda/Fałsz`, `A/B + C/D`, `Tak/Nie + uzasadnienie 1/2/3`) oraz wybór poziomu trudności.
- **60 parametrycznych wzorców zadań z 12 działów E8** (każde losowanie generuje nowe, spójne matematycznie dane liczbowe oraz realistyczne dystraktory wzorowane na błędach egzaminacyjnych CKE):
  1. Liczby, ułamki, podzielność i oś liczbowa
  2. Procenty, obniżki cen i proporcje
  3. Potęgi i notacja wykładnicza
  4. Pierwiastki kwadratowe i sześcienne
  5. Wyrażenia algebraiczne
  6. Równania i zadania tekstowe
  7. Prędkość, droga, czas i obliczenia zegarowe
  8. Układ współrzędnych na płaszczyźnie
  9. Geometria płaska (kąty, trójkąty, czworokąty, okrąg, tw. Pitagorasa)
  10. Geometria przestrzenna (graniastosłupy, ostrosłupy, siatki brył, poziom wody)
  11. Statystyka, tabele i diagramy słupkowe
  12. Prawdopodobieństwo i kombinatoryka
- **Dynamiczne rysunki pomocnicze w stylu CKE**: osie liczbowe, układy współrzędnych z kratką, trójkąty, trapezy, okrąg z cięciwą, siatki graniastosłupów ze strzałkami wymiarowymi, prostopadłościenne akwarium z wodą oraz diagramy słupkowe.
- **Podgląd na żywo i eksport do PDF (styl CKE)**:
  - **Arkusz dla ucznia PDF** – strona tytułowa z kratkami na KOD UCZNIA i PESEL, instrukcja dla zdającego, tabele `P/F` i `Tak/Nie + ponieważ 1/2/3`, kratka 5×5 mm na obliczenia i pole `Odpowiedź:` w zadaniach otwartych, numeracja `Strona X z Y`.
  - **Osobny Klucz Odpowiedzi i Rozwiązań PDF** – tabela szybkiego sprawdzania zadań zamkniętych, pełne rozwiązania krok po kroku oraz schemat punktowania CKE (`1 pkt / 2 pkt / 3 pkt`) dla zadań otwartych.
  - **Wymiana pojedynczego zadania** – na karcie *Lista zadań* możesz wymienić dowolne pojedyncze zadanie bez losowania całego arkusza od nowa.

---

## Jak uruchomić program lokalnie?

Wymagany jest **Python 3.10 lub nowszy**.

### Sposób 1 – Szybkie uruchomienie dwuklikiem
- **Windows**: kliknij dwukrotnie plik **`uruchom_windows.bat`** (przy pierwszym uruchomieniu skrypt sam utworzy środowisko `.venv` i pobierze wymagane biblioteki).
- **Linux / macOS**: uruchom w terminalu:
  ```bash
  ./uruchom_linux_mac.sh
  ```

### Sposób 2 – Ręczna instalacja w terminalu / wierszu poleceń
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

### Opcjonalny tryb linii poleceń (`--cli`)
Możesz również wygenerować komplet PDF bezpośrednio z terminala:
```bash
python main.py --cli --out zestaw_probny --variant "Wersja A" --seed 2026
```
Program zapisze pliki `zestaw_probny_ARKUSZ.pdf` oraz `zestaw_probny_KLUCZ.pdf`.
