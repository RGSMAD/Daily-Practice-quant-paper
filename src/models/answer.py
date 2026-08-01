"""
answer.py

Dataclass representing an answer corresponding
to a generated aptitude question.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.models.enums import QuestionType


@dataclass(slots=True)
class Answer:
    """
    Represents the answer to a
    generated aptitude question.
    """

    question_id: int

    question_type: QuestionType

    question: str

    answer: str