"""
history.py

Manages generated question history to prevent duplicates
across daily executions.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from src.config import settings
from src.models.question import Question
from src.utils.helpers import ensure_directory
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class HistoryManager:
    """Handles storing and checking generated questions."""

    def __init__(self) -> None:
        """Initialize history manager."""

        self.history_directory: Path = (
            settings.paths.history_dir
        )

        ensure_directory(
            self.history_directory
        )

        self.history_file: Path = (
            self.history_directory
            / settings.history.filename
        )

        self.questions: set[str] = set()

        self._load()


    def exists(
        self,
        question_text: str,
    ) -> bool:
        """Check whether a question already exists.

        Args:
            question_text:
                Question text to search.

        Returns:
            bool:
                True if question exists.
        """

        return question_text in self.questions


    def add(
        self,
        question_text: str,
    ) -> None:
        """Add a question to history.

        Args:
            question_text:
                Question text.
        """

        self.questions.add(
            question_text
        )


    def add_questions(
        self,
        questions: List[Question],
    ) -> None:
        """Add multiple questions.

        Args:
            questions:
                Generated questions.
        """

        for question in questions:
            self.add(
                question.question
            )


    def save(self) -> None:
        """Save history to JSON file."""

        data = {
            "generated_at": datetime.now().isoformat(),
            "total_questions": len(
                self.questions
            ),
            "questions": sorted(
                self.questions
            ),
        }

        with self.history_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        LOGGER.info(
            "Saved %s questions to history.",
            len(self.questions),
        )


    def _load(self) -> None:
        """Load previous question history."""

        if not self.history_file.exists():

            LOGGER.info(
                "No history file found. Starting fresh."
            )

            return


        try:

            with self.history_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)


            self.questions = set(
                data.get(
                    "questions",
                    [],
                )
            )


            LOGGER.info(
                "Loaded %s historical questions.",
                len(self.questions),
            )


        except (
            json.JSONDecodeError,
            OSError,
        ) as error:

            LOGGER.error(
                "Unable to load history: %s",
                error,
            )

            self.questions = set()