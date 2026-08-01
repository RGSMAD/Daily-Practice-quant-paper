"""
history.py

Question history management for the
Daily Aptitude Generator.
"""

from __future__ import annotations

import json

from datetime import (
    datetime,
    timedelta,
)
from pathlib import Path

from src.config import settings
from src.models.question import Question


class HistoryManager:
    """
    Manages generated question history.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize history manager.
        """

        self.history_file = (
            settings.paths.history_dir
            / settings.history.filename
        )

        self.settings = (
            settings.history
        )

        self.questions: list[
            Question
        ] = []

        settings.paths.history_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.load()


    def load(
        self,
    ) -> None:
        """
        Load history from disk.
        """

        if not self.settings.enabled:

            self.questions = []

            return


        if not self.history_file.exists():

            self.questions = []

            return


        try:

            with self.history_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(
                    file
                )

            self.questions = [
                Question.from_dict(
                    item
                )
                for item in data
            ]

        except (
            OSError,
            json.JSONDecodeError,
        ):

            self.questions = []


    def save(
        self,
    ) -> None:
        """
        Save history to disk.
        """

        if not self.settings.enabled:

            return


        self._cleanup()


        with self.history_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                [
                    question.to_dict()
                    for question
                    in self.questions
                ],
                file,
                indent=4,
                ensure_ascii=False,
            )


    def is_duplicate(
        self,
        question: Question,
    ) -> bool:
        """
        Check whether a question
        already exists.
        """

        return any(
            existing.fingerprint
            == question.fingerprint
            for existing
            in self.questions
        )


    def add_question(
        self,
        question: Question,
    ) -> bool:
        """
        Add a single question to history.

        Returns:
            True if added successfully.
            False if duplicate.
        """

        if not self.settings.enabled:

            return True

        if self.is_duplicate(
            question,
        ):

            return False

        self.questions.append(
            question
        )

        return True


    def add_questions(
        self,
        questions: list[
            Question
        ],
    ) -> None:
        """
        Add multiple questions to
        history.
        """

        for question in questions:

            self.add_question(
                question
            )


    def recent(
        self,
        days: int = 7,
    ) -> list[
        Question
    ]:
        """
        Return recently generated
        questions.
        """

        cutoff = (
            datetime.now()
            -
            timedelta(
                days=days
            )
        )

        return [
            question
            for question
            in self.questions
            if question.created_at
            >= cutoff
        ]


    def clear(
        self,
    ) -> None:
        """
        Clear all history.
        """

        self.questions.clear()

        if self.history_file.exists():

            self.history_file.unlink()



    def cleanup(
        self,
    ) -> None:
        """
        Perform history cleanup and
        save the updated history.
        """

        self._cleanup()

        self.save()



    def _cleanup(
        self,
    ) -> None:
        """
        Remove expired questions and
        limit history size.
        """

        expiry = (
            datetime.now()
            -
            timedelta(
                days=self.settings.retain_days
            )
        )

        self.questions = [
            question
            for question
            in self.questions
            if question.created_at
            >= expiry
        ]

        self.questions = (
            self.questions[
                -self.settings.max_records:
            ]
        )