"""Testy jednostkowe i integracyjne Generatora Zadań E8 – Matematyka (v2 – CKE 2019–2026)."""

from __future__ import annotations

import math
import random
import unittest

import pypdfium2 as pdfium

from e8_generator.cke_archive import (
    EMPIRICAL_STATS,
    HISTORICAL_CKE_EXAMS,
    compute_active_topic_probabilities,
    sample_topic_quotas_stratified,
)
from e8_generator.diagrams import render_diagram
from e8_generator.engine import (
    compute_config_topic_probabilities,
    generate_exam_sheet,
    replace_single_task,
)
from e8_generator.generators import REGISTRY
from e8_generator.models import CLOSED_SUBTYPES, TOPICS, ExamConfig
from e8_generator.pdf_exporter import build_exam_pdf_bytes, build_key_pdf_bytes


class TestE8Generator(unittest.TestCase):
    def test_all_topics_have_closed_and_open_templates(self):
        self.assertGreaterEqual(len(REGISTRY), 84)
        for topic in TOPICS:
            t_closed = [t for t in REGISTRY if t.topic_id == topic.id and t.points == 1]
            t_open2 = [t for t in REGISTRY if t.topic_id == topic.id and t.points == 2]
            t_open3 = [t for t in REGISTRY if t.topic_id == topic.id and t.points == 3]
            self.assertGreaterEqual(len(t_closed), 3, f"Za mało zadań zamkniętych w dziale {topic.id}")
            self.assertGreaterEqual(len(t_open2), 1, f"Brak zadań 2-pkt w dziale {topic.id}")
            self.assertGreaterEqual(len(t_open3), 1, f"Brak zadań 3-pkt w dziale {topic.id}")

    def test_every_template_randomized_stability_and_diagrams(self):
        rng = random.Random(12345)
        for tpl in REGISTRY:
            for run_idx in range(20):
                d = tpl.generator_fn(rng)
                self.assertTrue(d["stem"].strip())
                self.assertTrue(d["command"].strip())
                self.assertTrue(d["correct_answer"].strip())
                self.assertGreaterEqual(len(d["solution_steps"]), 1)
                if tpl.subtype == "abcd":
                    self.assertEqual(len(set(d["choices"].values())), 4, f"Zduplikowane dystraktory w {tpl.template_id}")
                    self.assertIn(d["correct_answer"], d["choices"])
                if run_idx == 0 and d.get("diagram") is not None:
                    img_path, w_px, h_px = render_diagram(d["diagram"])
                    self.assertTrue(img_path.endswith(".png"))
                    self.assertGreater(w_px, 80)
                    self.assertGreater(h_px, 50)

    def test_cke_archive_integrity_and_base_probabilities(self):
        self.assertEqual(len(HISTORICAL_CKE_EXAMS), 12)
        total_tasks = sum(len(s.tasks) for s in HISTORICAL_CKE_EXAMS)
        self.assertEqual(total_tasks, 240)

        prob_sum = sum(EMPIRICAL_STATS[t.id].base_probability for t in TOPICS)
        self.assertAlmostEqual(prob_sum, 1.0, places=9)
        for t in TOPICS:
            self.assertGreater(EMPIRICAL_STATS[t.id].total_tasks, 0)

    def test_equal_additive_redistribution_formula(self):
        all_ids = [t.id for t in TOPICS]

        # 1. Wykreślenie 1 działu (geometria_plaska = 20%) -> pozostałe 11 dostaje po +20%/11
        active_11 = [tid for tid in all_ids if tid != "geometria_plaska"]
        probs_11 = compute_active_topic_probabilities(active_11)
        self.assertEqual(probs_11["geometria_plaska"], 0.0)
        self.assertAlmostEqual(sum(probs_11.values()), 1.0, places=9)

        removed_p = EMPIRICAL_STATS["geometria_plaska"].base_probability
        expected_bonus = removed_p / 11.0
        for tid in active_11:
            expected_p = EMPIRICAL_STATS[tid].base_probability + expected_bonus
            self.assertAlmostEqual(probs_11[tid], expected_p, places=9)

        # 2. Wykreślenie 5 dowolnych działów -> pozostałe 7 dostaje po równo R / 7
        removed_5 = {"geometria_plaska", "liczby_dzialania", "potegi_notacja", "statystyka_diagramy", "prawdopodobienstwo"}
        active_7 = [tid for tid in all_ids if tid not in removed_5]
        probs_7 = compute_active_topic_probabilities(active_7)
        self.assertAlmostEqual(sum(probs_7.values()), 1.0, places=9)
        r_sum = sum(EMPIRICAL_STATS[tid].base_probability for tid in removed_5)
        for tid in all_ids:
            if tid in removed_5:
                self.assertEqual(probs_7[tid], 0.0)
            else:
                self.assertAlmostEqual(probs_7[tid], EMPIRICAL_STATS[tid].base_probability + r_sum / 7.0, places=9)

    def test_madow_stratified_quota_bounds_and_unbiased_convergence(self):
        rng = random.Random(2026)
        active = [t.id for t in TOPICS if t.id not in ("geometria_plaska", "uklad_wspolrzednych")]
        probs = compute_active_topic_probabilities(active)
        n_tasks = 20
        n_sim = 2500
        totals = {t.id: 0 for t in TOPICS}

        for _ in range(n_sim):
            q = sample_topic_quotas_stratified(rng, n_tasks, probs)
            self.assertEqual(sum(q.values()), n_tasks)
            for t in TOPICS:
                exact = n_tasks * probs[t.id]
                lo = math.floor(exact - 1e-9)
                hi = math.ceil(exact + 1e-9)
                self.assertGreaterEqual(q[t.id], lo)
                self.assertLessEqual(q[t.id], hi)
                totals[t.id] += q[t.id]

        for t in TOPICS:
            sim_share = totals[t.id] / (n_sim * n_tasks)
            self.assertAlmostEqual(sim_share, probs[t.id], delta=0.004)

    def test_engine_sheet_probability_adherence_and_mirror_sessions(self):
        # Sprawdź zbieżność pełnego silnika generate_exam_sheet przy wykreślonych 3 działach
        sel = [t.id for t in TOPICS if t.id not in ("geometria_przestrzenna", "pierwiastki", "prawdopodobienstwo")]
        cfg = ExamConfig(selected_topics=sel, include_diagrams=False)
        tgt = compute_config_topic_probabilities(cfg)
        acc = {t.id: 0 for t in TOPICS}
        n_runs = 200
        for i in range(n_runs):
            cfg.seed = 9000 + i
            sh = generate_exam_sheet(cfg)
            self.assertEqual(len(sh.tasks), 20)
            for task in sh.tasks:
                acc[task.topic_id] += 1

        for t in TOPICS:
            actual = acc[t.id] / (n_runs * 20)
            if t.id not in sel:
                self.assertEqual(acc[t.id], 0)
            else:
                self.assertAlmostEqual(actual, tgt[t.id], delta=0.009)

        # Sprawdź wszystkie 12 historycznych sesji w trybie mirror_session:<id>
        for sess in HISTORICAL_CKE_EXAMS:
            m_cfg = ExamConfig(
                distribution_mode=f"mirror_session:{sess.session_id}",
                include_diagrams=False,
                seed=101,
            )
            m_sheet = generate_exam_sheet(m_cfg)
            self.assertEqual(len(m_sheet.tasks), sess.total_tasks)

    def test_full_cke_omap100_sheet_and_pdf_export(self):
        cfg = ExamConfig(
            closed_count=14,
            open_2pt_count=2,
            open_3pt_count=4,
            include_cover_page=True,
            include_answer_card=True,
            seed=202605,
        )
        sheet = generate_exam_sheet(cfg)
        self.assertEqual(len(sheet.tasks), 20)
        self.assertEqual(sheet.total_points, 30)
        self.assertEqual([t.number for t in sheet.tasks], list(range(1, 21)))

        exam_pdf = build_exam_pdf_bytes(sheet)
        key_pdf = build_key_pdf_bytes(sheet)
        self.assertGreater(len(exam_pdf), 25_000)
        self.assertGreater(len(key_pdf), 25_000)

        doc_ex = pdfium.PdfDocument(exam_pdf)
        doc_key = pdfium.PdfDocument(key_pdf)
        # Strona 1 = okładka OMAP-100, strony środkowe = zadania, ostatnia = Karta Odpowiedzi
        self.assertGreaterEqual(len(doc_ex), 6)
        self.assertGreaterEqual(len(doc_key), 4)

    def test_single_topic_filtering_and_task_replacement(self):
        for topic in TOPICS:
            cfg = ExamConfig(
                selected_topics=[topic.id],
                closed_count=4,
                open_2pt_count=1,
                open_3pt_count=1,
                include_cover_page=False,
                include_answer_card=False,
                seed=99,
            )
            sheet = generate_exam_sheet(cfg)
            self.assertEqual(len(sheet.tasks), 6)
            for t in sheet.tasks:
                self.assertEqual(t.topic_id, topic.id)

            replaced = replace_single_task(sheet, 0)
            self.assertEqual(replaced.number, 1)
            self.assertEqual(replaced.points, 1)
            self.assertEqual(replaced.topic_id, topic.id)

    def test_only_specific_closed_subtype(self):
        for st in CLOSED_SUBTYPES:
            cfg = ExamConfig(
                closed_count=5,
                open_2pt_count=0,
                open_3pt_count=0,
                allowed_closed_subtypes=[st],
                include_cover_page=False,
                include_answer_card=False,
                seed=42,
            )
            sheet = generate_exam_sheet(cfg)
            self.assertEqual(len(sheet.tasks), 5)
            for t in sheet.tasks:
                self.assertEqual(t.subtype, st)


if __name__ == "__main__":
    unittest.main()
