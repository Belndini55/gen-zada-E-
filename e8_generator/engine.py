"""Silnik układania arkuszy i zestawów zadań zgodnie z wytycznymi CKE E8."""

from __future__ import annotations

import random
import time
from typing import List, Optional, Sequence

from .generators import REGISTRY
from .models import (
    CLOSED_SUBTYPES,
    TOPICS,
    ExamConfig,
    ExamSheet,
    Task,
    TaskTemplate,
)

TOPIC_ORDER = {t.id: idx for idx, t in enumerate(TOPICS)}


def _difficulty_weight(tpl: TaskTemplate, mode: str) -> float:
    if mode == "easy":
        return {1: 4.0, 2: 2.0, 3: 0.5}.get(tpl.difficulty, 1.0)
    if mode == "hard":
        return {1: 0.5, 2: 2.0, 3: 4.5}.get(tpl.difficulty, 1.0)
    return {1: 2.0, 2: 3.0, 3: 1.8}.get(tpl.difficulty, 1.0)


def _instantiate_template(tpl: TaskTemplate, rng: random.Random, number: int, include_diagrams: bool = True) -> Task:
    data = tpl.generator_fn(rng)
    diag = data.get("diagram") if include_diagrams else None
    # Jeśli zadanie wymaga rysunku z treści (np. siatka graniastosłupa), zachowaj rysunek nawet przy wyłączonych opcjonalnych,
    # chyba że użytkownik wyraźnie wyłączył rysunki – silnik najpierw filtruje szablony bez rysunków.
    if not include_diagrams and tpl.has_diagram:
        diag = data.get("diagram")

    return Task(
        number=number,
        topic_id=tpl.topic_id,
        subtype=tpl.subtype,
        points=tpl.points,
        difficulty=tpl.difficulty,
        template_id=tpl.template_id,
        cke_ref=tpl.cke_ref,
        stem=data["stem"],
        command=data["command"],
        table_data=data.get("table_data"),
        diagram=diag,
        choices=data.get("choices", {}),
        pf_statements=data.get("pf_statements", []),
        ab_cd_parts=data.get("ab_cd_parts", []),
        justification_data=data.get("justification_data", {}),
        correct_answer=data["correct_answer"],
        solution_steps=data.get("solution_steps", []),
        scoring_scheme=data.get("scoring_scheme", []),
        grid_height_mm=float(data.get("grid_height_mm", 52.0 if tpl.points == 2 else 62.0)),
    )


def _pick_weighted(rng: random.Random, candidates: Sequence[TaskTemplate], weights: Sequence[float]) -> TaskTemplate:
    total = sum(weights)
    if total <= 0:
        return rng.choice(list(candidates))
    r = rng.uniform(0, total)
    upto = 0.0
    for c, w in zip(candidates, weights):
        upto += w
        if upto >= r:
            return c
    return candidates[-1]


def _select_templates(
    rng: random.Random,
    pool: List[TaskTemplate],
    count: int,
    difficulty_mode: str,
    subtype_targets: Optional[dict[str, int]] = None,
) -> List[TaskTemplate]:
    """Wybiera `count` szablonów z `pool`, dbając o równomierne pokrycie działów i brak duplikatów."""
    if count <= 0 or not pool:
        return []

    chosen: List[TaskTemplate] = []
    used_ids: set[str] = set()
    topic_counts: dict[str, int] = {}
    subtype_counts: dict[str, int] = {}

    for _ in range(count):
        # Najpierw preferuj nieużyte jeszcze szablony; jeśli pula się wyczerpie, dopuść ponowne użycie z nowymi liczbami
        avail = [t for t in pool if t.template_id not in used_ids]
        if not avail:
            avail = list(pool)

        weights: List[float] = []
        for tpl in avail:
            w = _difficulty_weight(tpl, difficulty_mode)
            # Premia za rzadziej użyty dział (równomierny rozkład tematyczny jak w CKE)
            t_used = topic_counts.get(tpl.topic_id, 0)
            w *= 1.0 / (1.0 + 2.2 * t_used)

            # Dopasowanie proporcji podtypów zadań zamkniętych (ABCD / P-F / AB-CD / Uzasadnienie)
            if subtype_targets and tpl.subtype in subtype_targets:
                cur_s = subtype_counts.get(tpl.subtype, 0)
                tgt_s = subtype_targets[tpl.subtype]
                if cur_s < tgt_s:
                    w *= 2.4
                else:
                    w *= 0.35
            weights.append(w)

        picked = _pick_weighted(rng, avail, weights)
        chosen.append(picked)
        used_ids.add(picked.template_id)
        topic_counts[picked.topic_id] = topic_counts.get(picked.topic_id, 0) + 1
        subtype_counts[picked.subtype] = subtype_counts.get(picked.subtype, 0) + 1

    return chosen


def generate_exam_sheet(config: ExamConfig) -> ExamSheet:
    """Generuje kompletny arkusz zadań według podanej konfiguracji `ExamConfig`."""
    used_seed = config.seed if config.seed is not None else (int(time.time() * 1000) % 900_000 + 100_000)
    rng = random.Random(used_seed)

    topics = config.selected_topics if config.selected_topics else [t.id for t in TOPICS]
    topic_set = set(topics)

    allowed_closed = config.allowed_closed_subtypes if config.allowed_closed_subtypes else list(CLOSED_SUBTYPES)
    allowed_closed_set = set(allowed_closed)

    # Pula zadań zamkniętych
    closed_pool = [
        t for t in REGISTRY
        if t.points == 1 and t.topic_id in topic_set and t.subtype in allowed_closed_set
    ]
    if not config.include_diagrams:
        no_diag = [t for t in closed_pool if not t.has_diagram]
        if no_diag:
            closed_pool = no_diag
    if not closed_pool:
        # Awaryjny fallback, gdyby wybrano podtyp nieobecny w pojedynczym dziale
        closed_pool = [t for t in REGISTRY if t.points == 1 and t.topic_id in topic_set]

    # Docelowe proporcje podtypów zamkniętych (w stylu CKE: ~65% ABCD, reszta P/F, AB/CD, Uzasadnienie)
    c_total = max(0, config.closed_count)
    subtype_targets: dict[str, int] = {}
    if c_total > 0 and len(allowed_closed_set) > 1:
        rem = c_total
        if "pf" in allowed_closed_set:
            n_pf = max(1, round(c_total * 0.16))
            subtype_targets["pf"] = n_pf
            rem -= n_pf
        if "ab_cd" in allowed_closed_set and rem > 1:
            n_ab = max(1, round(c_total * 0.13))
            subtype_targets["ab_cd"] = n_ab
            rem -= n_ab
        if "uzasadnienie" in allowed_closed_set and rem > 1:
            n_uz = max(1, round(c_total * 0.11))
            subtype_targets["uzasadnienie"] = n_uz
            rem -= n_uz
        if "abcd" in allowed_closed_set:
            subtype_targets["abcd"] = max(1, rem)

    chosen_closed = _select_templates(rng, closed_pool, c_total, config.difficulty_mode, subtype_targets)
    # Posortuj zadania zamknięte zgodnie z naturalną kolejnością działów w arkuszach CKE
    chosen_closed.sort(key=lambda t: (TOPIC_ORDER.get(t.topic_id, 99), t.difficulty))

    # Pula zadań otwartych 2-punktowych i 3-punktowych
    open2_pool = [t for t in REGISTRY if t.points == 2 and t.topic_id in topic_set]
    open3_pool = [t for t in REGISTRY if t.points == 3 and t.topic_id in topic_set]
    if not config.include_diagrams:
        nd2 = [t for t in open2_pool if not t.has_diagram]
        nd3 = [t for t in open3_pool if not t.has_diagram]
        if nd2:
            open2_pool = nd2
        if nd3:
            open3_pool = nd3

    chosen_open2 = _select_templates(rng, open2_pool, max(0, config.open_2pt_count), config.difficulty_mode)
    chosen_open3 = _select_templates(rng, open3_pool, max(0, config.open_3pt_count), config.difficulty_mode)

    all_templates = chosen_closed + chosen_open2 + chosen_open3
    tasks: List[Task] = []
    for idx, tpl in enumerate(all_templates, start=1):
        tasks.append(_instantiate_template(tpl, rng, number=idx, include_diagrams=config.include_diagrams))

    return ExamSheet(config=config, used_seed=used_seed, tasks=tasks)


def replace_single_task(sheet: ExamSheet, task_index: int) -> Task:
    """Wymienia pojedyncze zadanie o indeksie `task_index` (0-based) na nowe losowe o tej samej punktacji."""
    old_task = sheet.tasks[task_index]
    rng = random.Random(int(time.time() * 1000000) ^ (task_index * 7919))

    topics = sheet.config.selected_topics if sheet.config.selected_topics else [t.id for t in TOPICS]
    topic_set = set(topics)
    existing_tpl_ids = {t.template_id for i, t in enumerate(sheet.tasks) if i != task_index}

    if old_task.points == 1:
        allowed_closed = set(sheet.config.allowed_closed_subtypes or CLOSED_SUBTYPES)
        pool = [t for t in REGISTRY if t.points == 1 and t.topic_id in topic_set and t.subtype in allowed_closed]
    else:
        pool = [t for t in REGISTRY if t.points == old_task.points and t.topic_id in topic_set]

    if not pool:
        pool = [t for t in REGISTRY if t.points == old_task.points]

    # Preferuj szablon inny niż dotychczasowy i nieużyty w reszcie arkusza
    fresh = [t for t in pool if t.template_id != old_task.template_id and t.template_id not in existing_tpl_ids]
    if not fresh:
        fresh = [t for t in pool if t.template_id != old_task.template_id]
    if not fresh:
        fresh = pool

    picked = rng.choice(fresh)
    new_task = _instantiate_template(picked, rng, number=old_task.number, include_diagrams=sheet.config.include_diagrams)
    sheet.tasks[task_index] = new_task
    return new_task
