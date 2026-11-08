"""Wspólny rejestr i funkcje pomocnicze dla szablonów zadań CKE E8."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from ..models import TaskTemplate

REGISTRY: List[TaskTemplate] = []


def register_template(
    template_id: str,
    topic_id: str,
    subtype: str,
    points: int,
    difficulty: int,
    cke_ref: str,
    has_diagram: bool = False,
) -> Callable[[Callable[[Any], Dict[str, Any]]], Callable[[Any], Dict[str, Any]]]:
    """Dekorator rejestrujący parametryczny generator zadania."""
    def decorator(fn: Callable[[Any], Dict[str, Any]]) -> Callable[[Any], Dict[str, Any]]:
        REGISTRY.append(
            TaskTemplate(
                template_id=template_id,
                topic_id=topic_id,
                subtype=subtype,
                points=points,
                difficulty=difficulty,
                cke_ref=cke_ref,
                has_diagram=has_diagram,
                generator_fn=fn,
            )
        )
        return fn
    return decorator
