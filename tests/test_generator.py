"""Testy jednostkowe i integracyjne Generatora Zadań E8 – Matematyka."""

from __future__ import annotations

import random
import unittest

import pypdfium2 as pdfium

from e8_generator.engine import generate_exam_sheet, replace_single_task
from e8_generator.generators import REGISTRY
from e8_generator.models import CLOSED_SUBTYPES, TOPICS, ExamConfig
from e8_generator.pdf_exporter import build_exam_pdf_bytes, build_key_pdf_bytes


class TestE8Generator(unittest.TestCase):
    def test_all_topics_have_closed_and_open_templates(self):
        self.assertGreaterEqual(len(REGISTRY), 60)
        for topic in TOPICS:
            t_closed = [t for t in REGISTRY if t.topic_id == topic.id and t.points == 1]
            t_open2 = [t for t in REGISTRY if t.topic_id == topic.id and t.points == 2]
            t_open3 = [t for t in REGISTRY if t.topic_id == topic.id and t.points == 3]
            self.assertGreaterEqual(len(t_closed), 3, f"Brak zadań zamkniętych w dziale {topic.id}")
            self.assertGreaterEqual(len(t_open2), 1, f"Brak zadań 2-pkt w dziale {topic.id}")
            self.assertGreaterEqual(len(t_open3), 1, f"Brak zadań 3-pkt w dziale {topic.id}")

    def test_every_template_randomized_stability(self):
        rng = random.Random(12345)
        for tpl in REGISTRY:
            for _ in range(10):
                d = tpl.generator_fn(rng)
                self.assertTrue(d["stem"].strip())
                self.assertTrue(d["command"].strip())
                self.assertTrue(d["correct_answer"].strip())
                self.assertGreaterEqual(len(d["solution_steps"]), 1)
                if tpl.subtype == "abcd":
                    self.assertEqual(len(set(d["choices"].values())), 4)
                    self.assertIn(d["correct_answer"], d["choices"])

    def test_full_cke_2025_2026_sheet_and_pdf_export(self):
        cfg = ExamConfig(
            closed_count=15,
            open_2pt_count=3,
            open_3pt_count=3,
            seed=777,
        )
        sheet = generate_exam_sheet(cfg)
        self.assertEqual(len(sheet.tasks), 21)
        self.assertEqual(sheet.total_points, 30)
        self.assertEqual([t.number for t in sheet.tasks], list(range(1, 22)))

        exam_pdf = build_exam_pdf_bytes(sheet)
        key_pdf = build_key_pdf_bytes(sheet)
        self.assertGreater(len(exam_pdf), 20_000)
        self.assertGreater(len(key_pdf), 20_000)

        doc_ex = pdfium.PdfDocument(exam_pdf)
        doc_key = pdfium.PdfDocument(key_pdf)
        self.assertGreaterEqual(len(doc_ex), 5)
        self.assertGreaterEqual(len(doc_key), 3)

    def test_single_topic_filtering_and_task_replacement(self):
        for topic in TOPICS:
            cfg = ExamConfig(
                selected_topics=[topic.id],
                closed_count=4,
                open_2pt_count=1,
                open_3pt_count=1,
                include_cover_page=False,
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
                seed=42,
            )
            sheet = generate_exam_sheet(cfg)
            self.assertEqual(len(sheet.tasks), 5)
            for t in sheet.tasks:
                self.assertEqual(t.subtype, st)


if __name__ == "__main__":
    unittest.main()
