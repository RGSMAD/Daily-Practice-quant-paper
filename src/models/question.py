"""
question.py

Dataclass representing a generated aptitude question.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

from models.enums import Difficulty, QuestionType


@dataclass(slots=True)
class Question:
    """
    Represents a single aptitude question.
    """

    id: str

    fingerprint: str

    question_type: QuestionType

    difficulty: Difficulty

    question: str

    answer: str

    explanation: str | None = None

    topic: str | None = None

    source: str | None = None

    created_at: datetime = (
        datetime.now()
    )


    def to_dict(self) -> dict[str, Any]:
        """
        Convert Question object into JSON-compatible data.
        """

        data = asdict(self)

        data["question_type"] = (
            self.question_type.value
        )

        data["difficulty"] = (
            self.difficulty.value
        )

        data["created_at"] = (
            self.created_at.isoformat()
        )

        return data


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Question":
        """
        Recreate Question object from JSON data.
        """

        return cls(
            id=data["id"],
            fingerprint=data["fingerprint"],
            question_type=QuestionType(
                data["question_type"]
            ),
            difficulty=Difficulty(
                data["difficulty"]
            ),
            question=data["question"],
            answer=data["answer"],
            explanation=data.get(
                "explanation"
            ),
            topic=data.get(
                "topic"
            ),
            source=data.get(
                "source"
            ),
            created_at=datetime.fromisoformat(
                data["created_at"]
            ),
        )