#!/usr/bin/env python3
"""Punkt wejścia programu: Generator Zadań E8 – Matematyka (styl CKE).

Uruchomienie okienkowe (domyślne):
    python main.py

Opcjonalne szybkie generowanie z linii poleceń:
    python main.py --cli --out arkusz_probny --seed 2026
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def run_cli(args: argparse.Namespace) -> int:
    from e8_generator.engine import generate_exam_sheet
    from e8_generator.models import TOPICS, ExamConfig
    from e8_generator.pdf_exporter import build_exam_pdf_bytes, build_key_pdf_bytes

    topics = [t.strip() for t in args.topics.split(",") if t.strip()] if args.topics else [t.id for t in TOPICS]
    cfg = ExamConfig(
        variant_code=args.variant,
        exam_code=args.exam_code,
        closed_count=args.closed,
        open_2pt_count=args.open2,
        open_3pt_count=args.open3,
        selected_topics=topics,
        distribution_mode=args.distribution,
        difficulty_mode=args.difficulty,
        include_cover_page=not args.no_cover,
        include_answer_card=not args.no_answer_card,
        seed=args.seed,
    )
    sheet = generate_exam_sheet(cfg)
    exam_pdf = build_exam_pdf_bytes(sheet)
    key_pdf = build_key_pdf_bytes(sheet)

    out_base = Path(args.out)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    exam_path = Path(f"{out_base}_ARKUSZ.pdf")
    key_path = Path(f"{out_base}_KLUCZ.pdf")
    exam_path.write_bytes(exam_pdf)
    key_path.write_bytes(key_pdf)

    print(f"Wygenerowano zestaw #{sheet.used_seed} ({len(sheet.tasks)} zadań, {sheet.total_points} pkt):")
    print(f"  Arkusz ucznia : {exam_path.resolve()}")
    print(f"  Klucz i rozw. : {key_path.resolve()}")
    return 0


def run_gui() -> int:
    import matplotlib
    from PyQt6.QtGui import QFontDatabase
    from PyQt6.QtWidgets import QApplication

    from e8_generator.gui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Generator Zadań E8 – Matematyka")

    # Załaduj czcionki DejaVu Sans z pakietu matplotlib (gwarancja polskich znaków na każdym systemie)
    ttf_dir = Path(matplotlib.__file__).resolve().parent / "mpl-data" / "fonts" / "ttf"
    for fname in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf"):
        fpath = ttf_dir / fname
        if fpath.exists():
            QFontDatabase.addApplicationFont(str(fpath))

    win = MainWindow()
    win.show()
    return app.exec()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generator Zadań E8 – Matematyka (wzorzec i statystyka CKE 2019–2026)")
    parser.add_argument("--cli", action="store_true", help="Wygeneruj pliki PDF bez otwierania okna graficznego")
    parser.add_argument("--out", default="arkusz_E8", help="Nazwa bazowa wyjściowych plików PDF (w trybie --cli)")
    parser.add_argument("--closed", type=int, default=14, help="Liczba zadań zamkniętych (1 pkt)")
    parser.add_argument("--open2", type=int, default=2, help="Liczba zadań otwartych krótkich (2 pkt)")
    parser.add_argument("--open3", type=int, default=4, help="Liczba zadań otwartych rozszerzonych (3 pkt)")
    parser.add_argument("--topics", default="", help="Lista ID działów oddzielona przecinkami (puste = wszystkie)")
    parser.add_argument(
        "--distribution",
        default="cke_probabilistic",
        help="Tryb rozkładu: cke_probabilistic (domyślny), uniform lub mirror_session:<id> (np. mirror_session:cke_2026_05)",
    )
    parser.add_argument("--difficulty", choices=["easy", "standard", "hard"], default="standard")
    parser.add_argument("--variant", default="Wersja A", help="Oznaczenie wersji na arkuszu")
    parser.add_argument("--exam-code", default="OMAP-100-2605", help="Kod arkusza CKE (np. OMAP-100-2605)")
    parser.add_argument("--seed", type=int, default=None, help="Opcjonalny numer zestawu (seed)")
    parser.add_argument("--no-cover", action="store_true", help="Pomiń stronę tytułową CKE")
    parser.add_argument("--no-answer-card", action="store_true", help="Pomiń Kartę Odpowiedzi na końcu arkusza")

    args = parser.parse_args()
    if args.cli:
        return run_cli(args)
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
