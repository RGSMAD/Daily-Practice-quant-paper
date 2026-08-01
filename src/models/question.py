"""
question.py

Dataclass representing a generated aptitude question.
"""

from dataclasses import dataclass
from typing import Optional

from models.enums import Difficulty, QuestionType


@dataclass(slots=True)
class Question:
    """
    Represents a single aptitude question.
    """

    id: int

    question_type: QuestionType

    difficulty: Difficulty

    question: str

    answer: str

    explanation: Optional[str] = None

    topic: Optional[str] = None