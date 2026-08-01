"""
question.py

Dataclass representing a generated aptitude question.
"""

from __future__ import annotations

import hashlib

from dataclasses import (
    asdict,
    dataclass,
    field,
)
from datetime import datetime
from typing import Any

from src.models.enums import (
    Difficulty,
    QuestionType,
)


@dataclass(slots=True)
class Question:
    """
    Represents a single aptitude question.
    """

    id: str

    question_type: QuestionType

    difficulty: Difficulty

    question: str

    answer: str

    explanation: str | None = None

    topic: str | None = None

    source: str | None = None

    created_at: datetime = field(
        default_factory=datetime.now
    )

    fingerprint: str = field(
        init=False
    )


    def __post_init__(self) -> None:
        """
        Generate a unique fingerprint used for
        duplicate detection.
        """

        content = (
            f"{self.question_type.value}|"
            f"{self.question}|"
            f"{self.answer}"
        )

        self.fingerprint = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()


    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert Question object into JSON-compatible
        dictionary.
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
        Recreate Question object from stored JSON data.
        """

        question = cls(
            id=data["id"],
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

        question.fingerprint = data[
            "fingerprint"
        ]

        return question