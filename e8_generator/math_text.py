"""Narzędzia formatowania polskiego tekstu matematycznego dla PDF (ReportLab) i GUI (Qt)."""

from __future__ import annotations

import base64
import hashlib
import html
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
from matplotlib.mathtext import math_to_image
from PIL import Image

# Dopasowanie kroju wzorów matematycznych do czcionki dokumentu (DejaVu Sans)
matplotlib.rcParams["mathtext.fontset"] = "dejavusans"

_MATH_CACHE_DIR = Path(tempfile.gettempdir()) / "e8_generator_math_cache"
_MATH_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_IMG_META_CACHE: Dict[Tuple[str, int, str], Tuple[str, float, float, str]] = {}


def pl_num(val: int | float | Fraction) -> str:
    """Formatuje liczbę po polsku (przecinek dziesiętny, znak minus Unicode, bez .0)."""
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return pl_num(val.numerator)
        val = float(val)
    if isinstance(val, float):
        if abs(val - round(val)) < 1e-9:
            val = int(round(val))
        else:
            s = f"{val:.6f}".rstrip("0").rstrip(".")
            s = s.replace(".", ",")
            if s.startswith("-"):
                s = "−" + s[1:]
            return s
    s = str(int(val))
    neg = s.startswith("-")
    digits = s[1:] if neg else s
    if len(digits) >= 5:
        parts = []
        while digits:
            parts.append(digits[-3:])
            digits = digits[:-3]
        digits = " ".join(reversed(parts))
    return ("−" + digits) if neg else digits


def pl_plural(n: int, one: str, few: str, many: str) -> str:
    """Polska odmiana rzeczownika po liczebniku całkowitym (np. 1 punkt, 2 punkty, 5 punktów)."""
    n_abs = abs(int(n))
    if n_abs == 1:
        return one
    if 10 <= (n_abs % 100) <= 21:
        return many
    if 2 <= (n_abs % 10) <= 4:
        return few
    return many


def frac_tex(num: int | str, den: int | str) -> str:
    """Zwraca zapis ułamka zwykłego w składni $...$."""
    return rf"$\frac{{{num}}}{{{den}}}$"


def mixed_frac_tex(whole: int, num: int, den: int) -> str:
    """Zwraca zapis liczby mieszanej w składni $...$."""
    if num == 0:
        return pl_num(whole)
    if whole == 0:
        return rf"$\frac{{{num}}}{{{den}}}$"
    sign = "−" if whole < 0 else ""
    return rf"{sign}{abs(whole)}$\frac{{{abs(num)}}}{{{den}}}$"


def shuffle_abcd(
    rng,
    correct_text: str,
    distractors: Sequence[str],
    preserve_order: bool = False,
) -> Tuple[Dict[str, str], str]:
    """Buduje słownik odpowiedzi A–D bez duplikatów i zwraca (choices, correct_letter)."""
    unique_items: List[str] = [correct_text]
    for d in distractors:
        if d not in unique_items:
            unique_items.append(d)
        if len(unique_items) == 4:
            break
    fallback_idx = 1
    while len(unique_items) < 4:
        cand = f"{correct_text} ({fallback_idx})"
        if cand not in unique_items:
            unique_items.append(cand)
        fallback_idx += 1

    if not preserve_order:
        rng.shuffle(unique_items)

    letters = ["A", "B", "C", "D"]
    choices = {letters[i]: unique_items[i] for i in range(4)}
    correct_letter = next(k for k, v in choices.items() if v == correct_text)
    return choices, correct_letter


def _render_mathtext_png(tex_inner: str, font_size_pt: float, color: str = "#111827") -> Tuple[str, float, float, str]:
    """Renderuje wyrażenie mathtext ($...$) do pliku PNG 300 DPI z pamięcią podręczną."""
    # Zamiana polskich przecinków w ułamkach dziesiętnych na bezpieczny zapis mathtext
    cleaned = tex_inner.strip()
    size_key = int(round(font_size_pt * 10))
    cache_key = (cleaned, size_key, color)
    if cache_key in _IMG_META_CACHE:
        path_str, w_pt, h_pt, b64 = _IMG_META_CACHE[cache_key]
        if os.path.exists(path_str):
            return path_str, w_pt, h_pt, b64

    digest = hashlib.md5(f"{cleaned}|{size_key}|{color}".encode("utf-8")).hexdigest()[:16]
    out_path = _MATH_CACHE_DIR / f"eq_{digest}.png"

    dpi = 300
    # Nieco większy rozmiar bazowy dla ułamków, aby licznik i mianownik były czytelne jak w CKE
    effective_pt = font_size_pt * (1.16 if (r"\frac" in cleaned or r"\dfrac" in cleaned) else 1.04)
    cleaned_norm = cleaned.replace(r"\dfrac", r"\frac")

    old_color = matplotlib.rcParams.get("text.color", "black")
    old_transp = matplotlib.rcParams.get("savefig.transparent", False)
    try:
        matplotlib.rcParams["text.color"] = color
        matplotlib.rcParams["savefig.transparent"] = True
        math_to_image(f"${cleaned_norm}$", str(out_path), dpi=dpi, format="png")
    finally:
        matplotlib.rcParams["text.color"] = old_color
        matplotlib.rcParams["savefig.transparent"] = old_transp

    with Image.open(out_path) as im:
        # Przytnij przezroczyste brzegi, zostawiając minimalny margines 2 px
        bbox = im.getbbox()
        if bbox:
            left = max(0, bbox[0] - 2)
            top = max(0, bbox[1] - 2)
            right = min(im.width, bbox[2] + 2)
            bottom = min(im.height, bbox[3] + 2)
            cropped = im.crop((left, top, right, bottom))
            cropped.save(out_path)
            w_px, h_px = cropped.size
        else:
            w_px, h_px = im.size

    # Przelicz piksele z 300 DPI na punkty typograficzne (72 pt/cal), skalując delikatnie pod effective_pt
    scale = (effective_pt / 10.0) * (72.0 / dpi)
    w_pt = w_px * (72.0 / dpi) * (effective_pt / 10.5)
    h_pt = h_px * (72.0 / dpi) * (effective_pt / 10.5)

    with open(out_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    posix_path = out_path.as_posix()
    _IMG_META_CACHE[cache_key] = (posix_path, w_pt, h_pt, b64)
    return posix_path, w_pt, h_pt, b64


_SIMPLE_TEX_RE = re.compile(r"^[A-Za-z0-9\s\+\-\=\<\>\(\)\[\]\,\.\:\;\^\°\%\/\*\_\\cdot\\times\\circ\\le\\ge\\neq\\approx]+$")


def _needs_image_render(tex_inner: str) -> bool:
    """Sprawdza, czy formuła wymaga obrazka (ułamki piętrowe, pierwiastki), czy wystarczy wektorowy tekst."""
    if any(tok in tex_inner for tok in (r"\frac", r"\dfrac", r"\sqrt", r"\overline", r"\pi")):
        return True
    return False


def _simple_tex_to_markup(tex_inner: str, target: str = "rl") -> str:
    """Konwertuje proste wyrażenie $...$ (bez ułamków piętrowych i pierwiastków) na czysty wektorowy zapis."""
    s = tex_inner.strip()
    s = s.replace(r"\;", " ")
    s = s.replace(r"\,", " ")
    s = s.replace(r"\quad", "  ")
    s = s.replace(r"\cdot", " · ")
    s = s.replace(r"\times", " × ")
    s = s.replace(r"\le", " ≤ ")
    s = s.replace(r"\ge", " ≥ ")
    s = s.replace(r"\neq", " ≠ ")
    s = s.replace(r"\approx", " ≈ ")
    s = s.replace(r"^\circ", "°")
    s = s.replace(r"\circ", "°")
    s = s.replace(r"\%", "%")
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\s+", " ", s)
    # Zamień zwykły minus matematyczny na półpauzę matematyczną Unicode
    s = s.replace("-", "−")

    s = html.escape(s)

    sup_tag = ("<super>", "</super>") if target == "rl" else ("<sup>", "</sup>")
    sub_tag = ("<sub>", "</sub>") if target == "rl" else ("<sub>", "</sub>")

    # Potęgi ^{...} oraz ^x
    s = re.sub(r"\^\{([^}]+)\}", lambda m: f"{sup_tag[0]}{m.group(1)}{sup_tag[1]}", s)
    s = re.sub(r"\^([−]?[A-Za-z0-9]+)", lambda m: f"{sup_tag[0]}{m.group(1)}{sup_tag[1]}", s)

    # Indeksy dolne _{...} oraz _x
    s = re.sub(r"_\{([^}]+)\}", lambda m: f"{sub_tag[0]}{m.group(1)}{sub_tag[1]}", s)
    s = re.sub(r"_([A-Za-z0-9]+)", lambda m: f"{sub_tag[0]}{m.group(1)}{sub_tag[1]}", s)

    # Kursywa dla pojedynczych zmiennych literowych (np. x, y, a, b, H, P, V, A, B, C)
    # ale nie ruszamy jednostek po spacji takich jak cm, km, min, h, kg, l, s
    UNITS = {"cm", "mm", "dm", "km", "m", "kg", "dag", "g", "t", "min", "sek", "godz", "h", "s", "l", "ml", "zł", "gr"}

    def _italicize_vars(match: re.Match) -> str:
        word = match.group(0)
        if word in UNITS or word in {"super", "sub", "sup"}:
            return word
        return f"<i>{word}</i>"

    # Italizuj tokeny literowe poza tagami HTML oraz poza encjami XML (&lt;, &gt;, &amp;)
    parts = re.split(r"(<[^>]+>|&[A-Za-z0-9#]+;)", s)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"(?<![A-Za-z])[A-Za-z]+(?![A-Za-z])", _italicize_vars, parts[i])
    return "".join(parts)


def _format_plain_segment(seg: str, target: str = "rl") -> str:
    """Formatuje zwykły tekst poza $...$ (obsługuje **pogrubienie**, *kursywę* oraz potęgi cm^2/cm^3)."""
    seg = seg.replace(" -> ", " → ")
    escaped = html.escape(seg)
    sup_tag = ("<super>", "</super>") if target == "rl" else ("<sup>", "</sup>")
    escaped = re.sub(r"\^\{([^}]+)\}", lambda m: f"{sup_tag[0]}{m.group(1)}{sup_tag[1]}", escaped)
    escaped = re.sub(r"\^([0-9]+)", lambda m: f"{sup_tag[0]}{m.group(1)}{sup_tag[1]}", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", escaped)
    escaped = escaped.replace("\n", "<br/>")
    return escaped


def to_rl_markup(text: str, font_size: float = 10.0) -> Tuple[str, float]:
    """Konwertuje tekst z formułami $...$ na znaczniki ReportLab Paragraph.

    Zwraca krotkę: (markup_xml, max_inline_math_height_pt).
    Dzięki max_inline_math_height_pt styl akapitu może dobrać odpowiedni leading (interlinię).
    """
    if not text:
        return "", 0.0

    tokens = re.split(r"(\$[^\$]+\$)", text)
    out: List[str] = []
    max_h = 0.0

    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("$") and tok.endswith("$") and len(tok) >= 2:
            inner = tok[1:-1]
            if _needs_image_render(inner):
                path_str, w_pt, h_pt, _ = _render_mathtext_png(inner, font_size)
                max_h = max(max_h, h_pt)
                valign = f"{-0.34 * h_pt:.1f}" if (r"\frac" in inner or r"\dfrac" in inner) else f"{-0.16 * h_pt:.1f}"
                out.append(
                    f'<img src="{path_str}" width="{w_pt:.2f}" height="{h_pt:.2f}" valign="{valign}"/>'
                )
            else:
                out.append(_simple_tex_to_markup(inner, target="rl"))
        else:
            out.append(_format_plain_segment(tok, target="rl"))

    return "".join(out), max_h


def to_qt_html(text: str, font_size: float = 10.5) -> str:
    """Konwertuje tekst z formułami $...$ na bogaty HTML wyświetlany w kartach zadań PyQt6."""
    if not text:
        return ""

    tokens = re.split(r"(\$[^\$]+\$)", text)
    out: List[str] = []

    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("$") and tok.endswith("$") and len(tok) >= 2:
            inner = tok[1:-1]
            if _needs_image_render(inner):
                _, w_pt, h_pt, b64 = _render_mathtext_png(inner, font_size)
                w_px = max(8, int(round(w_pt * 1.38)))
                h_px = max(8, int(round(h_pt * 1.38)))
                out.append(
                    f'<img src="data:image/png;base64,{b64}" width="{w_px}" height="{h_px}" style="vertical-align: middle;"/>'
                )
            else:
                out.append(_simple_tex_to_markup(inner, target="qt"))
        else:
            out.append(_format_plain_segment(tok, target="qt"))

    return "".join(out)
