"""Silnik układania arkuszy i zestawów zadań zgodnie z wytycznymi i statystyką CKE E8 (2019–2026).

Zawiera pamięć antypowtórzeniową sesji (`_RECENT_TEMPLATE_IDS` oraz `_RECENT_STEM_HASHES`),
dzięki której kolejne generowane arkusze tworzą za każdym razem świeże, niepowtarzające się zadania,
przy jednoczesnym zachowaniu pełnej powtarzalności deterministycznej, gdy użytkownik poda jawny `seed`.
"""

from __future__ import annotations

from collections import deque
import hashlib
import random
from typing import Deque, Dict, List, Optional, Sequence, Tuple

from .cke_archive import (
    EMPIRICAL_STATS,
    SESSION_BY_ID,
    compute_active_topic_probabilities,
    compute_empirical_closed_subtype_shares,
    sample_topic_quotas_stratified,
)
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

_SYS_RNG = random.SystemRandom()
_RECENT_TEMPLATE_IDS: Deque[str] = deque(maxlen=60)
_RECENT_STEM_HASHES: Deque[str] = deque(maxlen=280)


def reset_recent_history() -> None:
    """Czyści pamięć ostatnio wygenerowanych szablonów i treści zadań."""
    _RECENT_TEMPLATE_IDS.clear()
    _RECENT_STEM_HASHES.clear()


def _stem_fingerprint(stem: str, command: str) -> str:
    return hashlib.md5(f"{stem}||{command}".encode("utf-8")).hexdigest()[:16]


def _difficulty_weight(tpl: TaskTemplate, mode: str) -> float:
    if mode == "easy":
        return {1: 4.0, 2: 2.0, 3: 0.5}.get(tpl.difficulty, 1.0)
    if mode == "hard":
        return {1: 0.5, 2: 2.0, 3: 4.5}.get(tpl.difficulty, 1.0)
    return {1: 2.0, 2: 3.0, 3: 1.8}.get(tpl.difficulty, 1.0)


def _instantiate_template(
    tpl: TaskTemplate,
    rng: random.Random,
    number: int,
    include_diagrams: bool = True,
    avoid_recent_stems: bool = False,
    sheet_stem_hashes: Optional[set[str]] = None,
) -> Task:
    data = tpl.generator_fn(rng)
    fp = _stem_fingerprint(data["stem"], data["command"])
    if avoid_recent_stems or sheet_stem_hashes is not None:
        recent_set = set(_RECENT_STEM_HASHES) if avoid_recent_stems else set()
        local_set = sheet_stem_hashes or set()
        for _ in range(10):
            if fp not in recent_set and fp not in local_set:
                break
            data = tpl.generator_fn(rng)
            fp = _stem_fingerprint(data["stem"], data["command"])
        if sheet_stem_hashes is not None:
            sheet_stem_hashes.add(fp)
        if avoid_recent_stems:
            _RECENT_STEM_HASHES.append(fp)

    diag = data.get("diagram") if include_diagrams else None
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
    r = rng.uniform(0.0, total)
    upto = 0.0
    for c, w in zip(candidates, weights):
        upto += w
        if upto >= r:
            return c
    return candidates[-1]


def compute_config_topic_probabilities(config: ExamConfig) -> Dict[str, float]:
    """Zwraca docelowy rozkład prawdopodobieństwa działów dla bieżącej konfiguracji.

    - W trybie `"uniform"`: równe prawdopodobieństwo `1 / |S|` dla każdego zaznaczonego działu.
    - W trybie `"cke_probabilistic"` oraz `"mirror_session:..."`: empiryczne prawdopodobieństwo CKE
      z 12 arkuszy (2019–2026), a po wykreśleniu dowolnych działów ich łączna pula procentowa jest
      rozdzielana po równo pomiędzy wszystkie pozostałe aktywne działy: `p'_i = p_i + R / |S|`.
    """
    active = config.selected_topics if config.selected_topics else [t.id for t in TOPICS]
    active_set = [t.id for t in TOPICS if t.id in set(active)]
    if not active_set:
        active_set = [t.id for t in TOPICS]

    if config.distribution_mode == "uniform":
        eq = 1.0 / len(active_set)
        return {t.id: (eq if t.id in active_set else 0.0) for t in TOPICS}
    return compute_active_topic_probabilities(active_set)


def _split_quotas_into_closed_and_open(
    rng: random.Random,
    total_quotas: Dict[str, int],
    closed_count: int,
    open2_count: int,
    open3_count: int,
) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
    """Rozdziela łączną kwotę zadań `total_quotas[tid]` na zamknięte, otwarte 2 pkt i otwarte 3 pkt."""
    rem = dict(total_quotas)
    open2_q = {tid: 0 for tid in total_quotas}
    open3_q = {tid: 0 for tid in total_quotas}

    def _open_affinity(tid: str, already_open: int) -> float:
        st = EMPIRICAL_STATS.get(tid)
        if st and st.total_tasks > 0:
            base_aff = (st.open_tasks + 0.12) / (st.total_tasks + 0.6)
        else:
            base_aff = 0.25
        return base_aff / (1.0 + 1.8 * already_open)

    for target_dict, count in ((open3_q, open3_count), (open2_q, open2_count)):
        for _ in range(max(0, count)):
            avail_tids = [tid for tid, q in rem.items() if q > 0]
            if not avail_tids:
                break
            weights = [
                rem[tid] * _open_affinity(tid, open2_q[tid] + open3_q[tid])
                for tid in avail_tids
            ]
            total_w = sum(weights)
            r = rng.uniform(0.0, total_w)
            acc = 0.0
            picked_tid = avail_tids[-1]
            for tid, w in zip(avail_tids, weights):
                acc += w
                if acc >= r:
                    picked_tid = tid
                    break
            target_dict[picked_tid] += 1
            rem[picked_tid] -= 1

    closed_q = rem
    return closed_q, open2_q, open3_q


def _pick_template_for_slot(
    rng: random.Random,
    topic_id: str,
    points: int,
    include_diagrams: bool,
    difficulty_mode: str,
    used_template_ids: set[str],
    allowed_closed_set: Optional[set[str]] = None,
    preferred_subtype: Optional[str] = None,
    active_topic_set: Optional[set[str]] = None,
    avoid_recent_session: bool = False,
) -> TaskTemplate:
    """Dobiera szablon dla konkretnego działu i liczby punktów, unikając powtórzeń w arkuszu i między arkuszami."""
    if points == 1:
        allowed = allowed_closed_set or set(CLOSED_SUBTYPES)
        pool = [t for t in REGISTRY if t.points == 1 and t.topic_id == topic_id and t.subtype in allowed]
        if not pool and active_topic_set:
            pool = [t for t in REGISTRY if t.points == 1 and t.topic_id in active_topic_set and t.subtype in allowed]
        if not pool:
            pool = [t for t in REGISTRY if t.points == 1 and t.topic_id == topic_id]
    else:
        pool = [t for t in REGISTRY if t.points == points and t.topic_id == topic_id]
        if not pool:
            pool = [t for t in REGISTRY if t.is_open and t.topic_id == topic_id]

    if not include_diagrams:
        no_diag = [t for t in pool if not t.has_diagram]
        if no_diag:
            pool = no_diag

    if not pool:
        pool = [t for t in REGISTRY if t.points == points]

    fresh_in_sheet = [t for t in pool if t.template_id not in used_template_ids]
    avail = fresh_in_sheet if fresh_in_sheet else pool

    recent_set = set(_RECENT_TEMPLATE_IDS) if avoid_recent_session else set()
    if recent_set:
        unseen_recently = [t for t in avail if t.template_id not in recent_set]
        if unseen_recently:
            avail = unseen_recently

    weights: List[float] = []
    for tpl in avail:
        w = _difficulty_weight(tpl, difficulty_mode)
        if preferred_subtype and tpl.subtype == preferred_subtype:
            w *= 4.0
        if recent_set and tpl.template_id in recent_set:
            w *= 0.1
        weights.append(w)

    picked = _pick_weighted(rng, avail, weights)
    used_template_ids.add(picked.template_id)
    if avoid_recent_session:
        _RECENT_TEMPLATE_IDS.append(picked.template_id)
    return picked


def _generate_mirror_session_templates(
    rng: random.Random,
    session_id: str,
    active_set: set[str],
    topic_probs: Dict[str, float],
    allowed_closed_set: set[str],
    include_diagrams: bool,
    difficulty_mode: str,
    avoid_recent_session: bool = False,
) -> List[TaskTemplate]:
    """Tworzy zestaw NOWYCH zadań według rozkładu działów i punktów wybranej historycznej sesji CKE."""
    session = SESSION_BY_ID[session_id]

    unchecked_indices = [idx for idx, ht in enumerate(session.tasks) if ht.topic_id not in active_set]
    replacement_topics: List[str] = []
    if unchecked_indices:
        rep_quotas = sample_topic_quotas_stratified(rng, len(unchecked_indices), topic_probs)
        for tid, cnt in rep_quotas.items():
            replacement_topics.extend([tid] * cnt)
        rng.shuffle(replacement_topics)

    rep_ptr = 0
    used_ids: set[str] = set()
    chosen: List[TaskTemplate] = []

    for ht in session.tasks:
        if ht.topic_id in active_set:
            tid = ht.topic_id
        else:
            tid = replacement_topics[rep_ptr]
            rep_ptr += 1

        pts = 1 if ht.points == 1 else min(3, max(2, ht.points))
        pref_sub = ht.subtype if (pts == 1 and ht.subtype in allowed_closed_set) else None
        tpl = _pick_template_for_slot(
            rng=rng,
            topic_id=tid,
            points=pts,
            include_diagrams=include_diagrams,
            difficulty_mode=difficulty_mode,
            used_template_ids=used_ids,
            allowed_closed_set=allowed_closed_set,
            preferred_subtype=pref_sub,
            active_topic_set=active_set,
            avoid_recent_session=avoid_recent_session,
        )
        chosen.append(tpl)

    return chosen


def generate_exam_sheet(config: ExamConfig) -> ExamSheet:
    """Generuje kompletny arkusz NOWYCH zadań według podanej konfiguracji `ExamConfig`."""
    use_session_memory = config.seed is None
    used_seed = config.seed if config.seed is not None else _SYS_RNG.randint(100_000, 999_999)
    rng = random.Random(used_seed)

    topics = config.selected_topics if config.selected_topics else [t.id for t in TOPICS]
    active_set = set(topics)
    if not active_set:
        active_set = {t.id for t in TOPICS}

    allowed_closed = config.allowed_closed_subtypes if config.allowed_closed_subtypes else list(CLOSED_SUBTYPES)
    allowed_closed_set = set(allowed_closed)

    topic_probs = compute_config_topic_probabilities(config)
    sheet_stems: set[str] = set()

    if config.distribution_mode.startswith("mirror_session:"):
        sess_id = config.distribution_mode.split(":", 1)[1]
        if sess_id in SESSION_BY_ID:
            all_templates = _generate_mirror_session_templates(
                rng=rng,
                session_id=sess_id,
                active_set=active_set,
                topic_probs=topic_probs,
                allowed_closed_set=allowed_closed_set,
                include_diagrams=config.include_diagrams,
                difficulty_mode=config.difficulty_mode,
                avoid_recent_session=use_session_memory,
            )
            tasks = [
                _instantiate_template(
                    tpl,
                    rng,
                    number=i,
                    include_diagrams=config.include_diagrams,
                    avoid_recent_stems=use_session_memory,
                    sheet_stem_hashes=sheet_stems,
                )
                for i, tpl in enumerate(all_templates, start=1)
            ]
            return ExamSheet(
                config=config,
                used_seed=used_seed,
                tasks=tasks,
                topic_probabilities=topic_probs,
            )

    c_total = max(0, config.closed_count)
    o2_total = max(0, config.open_2pt_count)
    o3_total = max(0, config.open_3pt_count)
    n_total = c_total + o2_total + o3_total

    total_quotas = sample_topic_quotas_stratified(rng, n_total, topic_probs)

    closed_q, open2_q, open3_q = _split_quotas_into_closed_and_open(
        rng=rng,
        total_quotas=total_quotas,
        closed_count=c_total,
        open2_count=o2_total,
        open3_count=o3_total,
    )

    active_sub_shares = compute_empirical_closed_subtype_shares(list(allowed_closed_set))
    closed_subtype_quotas = sample_topic_quotas_stratified(rng, c_total, active_sub_shares)
    desired_subtypes: List[str] = []
    for s_key in CLOSED_SUBTYPES:
        desired_subtypes.extend([s_key] * closed_subtype_quotas.get(s_key, 0))
    rng.shuffle(desired_subtypes)

    used_ids: set[str] = set()

    closed_topic_slots: List[str] = []
    for t in TOPICS:
        closed_topic_slots.extend([t.id] * closed_q.get(t.id, 0))
    closed_topic_slots.sort(
        key=lambda tid: EMPIRICAL_STATS[tid].avg_relative_position + rng.uniform(-0.045, 0.045)
        if tid in EMPIRICAL_STATS
        else 0.5
    )

    chosen_closed: List[TaskTemplate] = []
    for idx, tid in enumerate(closed_topic_slots):
        pref_sub = desired_subtypes[idx] if idx < len(desired_subtypes) else None
        tpl = _pick_template_for_slot(
            rng=rng,
            topic_id=tid,
            points=1,
            include_diagrams=config.include_diagrams,
            difficulty_mode=config.difficulty_mode,
            used_template_ids=used_ids,
            allowed_closed_set=allowed_closed_set,
            preferred_subtype=pref_sub,
            active_topic_set=active_set,
            avoid_recent_session=use_session_memory,
        )
        chosen_closed.append(tpl)

    chosen_open2: List[TaskTemplate] = []
    open2_slots = [t.id for t in TOPICS for _ in range(open2_q.get(t.id, 0))]
    open2_slots.sort(key=lambda tid: EMPIRICAL_STATS[tid].avg_relative_position if tid in EMPIRICAL_STATS else 0.5)
    for tid in open2_slots:
        chosen_open2.append(
            _pick_template_for_slot(
                rng=rng,
                topic_id=tid,
                points=2,
                include_diagrams=config.include_diagrams,
                difficulty_mode=config.difficulty_mode,
                used_template_ids=used_ids,
                avoid_recent_session=use_session_memory,
            )
        )

    chosen_open3: List[TaskTemplate] = []
    open3_slots = [t.id for t in TOPICS for _ in range(open3_q.get(t.id, 0))]
    open3_slots.sort(key=lambda tid: EMPIRICAL_STATS[tid].avg_relative_position if tid in EMPIRICAL_STATS else 0.5)
    for tid in open3_slots:
        chosen_open3.append(
            _pick_template_for_slot(
                rng=rng,
                topic_id=tid,
                points=3,
                include_diagrams=config.include_diagrams,
                difficulty_mode=config.difficulty_mode,
                used_template_ids=used_ids,
                avoid_recent_session=use_session_memory,
            )
        )

    all_templates = chosen_closed + chosen_open2 + chosen_open3
    tasks: List[Task] = []
    for idx, tpl in enumerate(all_templates, start=1):
        tasks.append(
            _instantiate_template(
                tpl,
                rng,
                number=idx,
                include_diagrams=config.include_diagrams,
                avoid_recent_stems=use_session_memory,
                sheet_stem_hashes=sheet_stems,
            )
        )

    return ExamSheet(
        config=config,
        used_seed=used_seed,
        tasks=tasks,
        topic_probabilities=topic_probs,
    )


def replace_single_task(sheet: ExamSheet, task_index: int) -> Task:
    """Wymienia pojedyncze zadanie o indeksie `task_index` (0-based) na nowe losowe o tej samej punktacji."""
    old_task = sheet.tasks[task_index]
    rng = random.Random(_SYS_RNG.randint(1, 10_000_000) ^ (task_index * 7919))

    topics = sheet.config.selected_topics if sheet.config.selected_topics else [t.id for t in TOPICS]
    topic_set = set(topics)
    existing_tpl_ids = {t.template_id for i, t in enumerate(sheet.tasks) if i != task_index}
    allowed_closed = set(sheet.config.allowed_closed_subtypes or CLOSED_SUBTYPES)
    recent_set = set(_RECENT_TEMPLATE_IDS)

    if old_task.topic_id in topic_set:
        if old_task.points == 1:
            same_topic_pool = [
                t for t in REGISTRY
                if t.points == 1 and t.topic_id == old_task.topic_id and t.subtype in allowed_closed
                and t.template_id != old_task.template_id and t.template_id not in existing_tpl_ids
            ]
        else:
            same_topic_pool = [
                t for t in REGISTRY
                if t.points == old_task.points and t.topic_id == old_task.topic_id
                and t.template_id != old_task.template_id and t.template_id not in existing_tpl_ids
            ]
        if same_topic_pool:
            unseen = [t for t in same_topic_pool if t.template_id not in recent_set]
            picked = rng.choice(unseen if unseen else same_topic_pool)
            _RECENT_TEMPLATE_IDS.append(picked.template_id)
            new_task = _instantiate_template(
                picked,
                rng,
                number=old_task.number,
                include_diagrams=sheet.config.include_diagrams,
                avoid_recent_stems=True,
            )
            sheet.tasks[task_index] = new_task
            return new_task

    if old_task.points == 1:
        pool = [t for t in REGISTRY if t.points == 1 and t.topic_id in topic_set and t.subtype in allowed_closed]
    else:
        pool = [t for t in REGISTRY if t.points == old_task.points and t.topic_id in topic_set]

    if not pool:
        pool = [t for t in REGISTRY if t.points == old_task.points]

    fresh = [t for t in pool if t.template_id != old_task.template_id and t.template_id not in existing_tpl_ids]
    if not fresh:
        fresh = [t for t in pool if t.template_id != old_task.template_id]
    if not fresh:
        fresh = pool

    unseen_fresh = [t for t in fresh if t.template_id not in recent_set]
    if unseen_fresh:
        fresh = unseen_fresh

    probs = sheet.topic_probabilities or compute_config_topic_probabilities(sheet.config)
    weights = [max(0.01, probs.get(t.topic_id, 0.05)) for t in fresh]
    picked = _pick_weighted(rng, fresh, weights)
    _RECENT_TEMPLATE_IDS.append(picked.template_id)
    new_task = _instantiate_template(
        picked,
        rng,
        number=old_task.number,
        include_diagrams=sheet.config.include_diagrams,
        avoid_recent_stems=True,
    )
    sheet.tasks[task_index] = new_task
    return new_task
