"""
history.py

Question history management for the
Daily Aptitude Generator.

History lifecycle:

Monday - Saturday
    |
    | Generate daily questions
    | Check against current week's history
    | Add new questions
    | Save questions_history.json
    v
history/questions_history.json
    |
    | Sunday
    | Read previous six days
    | Generate weekly revision
    | Send revision email
    v
Clear current week's history
    |
    +--> Clear in-memory questions
    |
    +--> Remove questions_history.json

IMPORTANT:

- save() NEVER performs cleanup.
- History is retained throughout the week.
- Cleanup is performed explicitly through clear().
- No active.json is used.
- No retention-based cleanup is performed here.
"""

from __future__ import annotations

import json

from pathlib import Path

from src.config import settings
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class HistoryManager:
    """
    Manages generated question history.

    The history represents the questions generated during
    the current weekly cycle.

    Monday-Saturday questions are retained so that:

    1. Newly generated questions do not duplicate earlier
       questions from the same week.
    2. Sunday's revision workflow can select questions
       from the previous six days.

    History is cleared explicitly after the Sunday revision
    workflow has completed successfully.
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self) -> None:
        """
        Initialize the history manager.
        """

        self.settings = settings.history

        self.history_directory: Path = (
            settings.paths.history_dir
        )

        self.history_file: Path = (
            self.history_directory
            / self.settings.active_file
        )

        self.questions: list[Question] = []

        self.history_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.load()

    # =====================================================
    # LOAD
    # =====================================================

    def load(self) -> None:
        """
        Load question history from disk.

        If history is disabled or the history file does
        not exist, an empty history is used.
        """

        if not self.settings.enabled:

            self.questions = []

            LOGGER.info(
                "Question history is disabled."
            )

            return

        if not self.history_file.exists():

            self.questions = []

            LOGGER.info(
                "No question history file found: %s",
                self.history_file,
            )

            return

        try:

            with self.history_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if not isinstance(data, list):

                LOGGER.warning(
                    "Invalid history format in %s. "
                    "Expected a list.",
                    self.history_file,
                )

                self.questions = []

                return

            self.questions = [
                Question.from_dict(item)
                for item in data
            ]

            LOGGER.info(
                "Loaded %s questions from history.",
                len(self.questions),
            )

        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ):

            LOGGER.exception(
                "Failed to load question history "
                "from %s.",
                self.history_file,
            )

            self.questions = []

    # =====================================================
    # SAVE
    # =====================================================

    def save(self) -> None:
        """
        Save the current history to disk.

        IMPORTANT:

        This method does NOT perform cleanup.

        All questions generated during the current week
        must remain available until Sunday's revision
        workflow has completed.
        """

        if not self.settings.enabled:

            return

        self.history_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            with self.history_file.open(
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    [
                        question.to_dict()
                        for question in self.questions
                    ],
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            LOGGER.info(
                "Saved %s questions to history: %s",
                len(self.questions),
                self.history_file,
            )

        except OSError:

            LOGGER.exception(
                "Failed to save question history "
                "to %s.",
                self.history_file,
            )

            raise

    # =====================================================
    # DUPLICATE CHECK
    # =====================================================

    def is_duplicate(
        self,
        question: Question,
    ) -> bool:
        """
        Check whether a question already exists
        in the current weekly history.

        Args:
            question:
                Question to check.

        Returns:
            True:
                Question already exists.

            False:
                Question is new.
        """

        if not self.settings.enabled:

            return False

        return any(
            existing.fingerprint
            == question.fingerprint
            for existing in self.questions
        )

    # =====================================================
    # ADD SINGLE QUESTION
    # =====================================================

    def add_question(
        self,
        question: Question,
    ) -> bool:
        """
        Add a single question to history.

        Duplicate questions are not added.

        Args:
            question:
                Question to add.

        Returns:
            True:
                Question was added.

            False:
                Question was rejected because it
                already exists.
        """

        if not self.settings.enabled:

            return True

        if self.is_duplicate(question):

            LOGGER.debug(
                "Duplicate question rejected: %s",
                question.question,
            )

            return False

        self.questions.append(question)

        return True

    # =====================================================
    # ADD MULTIPLE QUESTIONS
    # =====================================================

    def add_questions(
        self,
        questions: list[Question],
    ) -> None:
        """
        Add multiple questions to history.

        Duplicate questions are skipped.
        """

        if not self.settings.enabled:

            return

        added_count = 0
        duplicate_count = 0

        for question in questions:

            if self.add_question(question):

                added_count += 1

            else:

                duplicate_count += 1

        LOGGER.info(
            "History update completed: "
            "%s added, %s duplicates skipped.",
            added_count,
            duplicate_count,
        )

    # =====================================================
    # RECENT QUESTIONS
    # =====================================================

    def recent(
        self,
        days: int = 7,
    ) -> list[Question]:
        """
        Return questions generated within the
        specified number of days.

        This method does NOT modify history.

        Args:
            days:
                Number of days to look back.

        Returns:
            List of recent questions.
        """

        if days <= 0:

            return []

        from datetime import datetime, timedelta

        cutoff = (
            datetime.now()
            - timedelta(days=days)
        )

        return [
            question
            for question in self.questions
            if question.created_at >= cutoff
        ]

    # =====================================================
    # WEEKLY QUESTIONS
    # =====================================================

    def weekly_questions(
        self,
    ) -> list[Question]:
        """
        Return all questions currently stored
        in the weekly history.

        Questions are returned in creation order.

        This is primarily used by the Sunday revision
        workflow.
        """

        return sorted(
            self.questions,
            key=lambda question: question.created_at,
        )

    # =====================================================
    # COUNT
    # =====================================================

    def count(self) -> int:
        """
        Return the number of questions currently
        stored in history.
        """

        return len(self.questions)

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self) -> None:
        """
        Completely clear the current weekly history.

        This operation:

        1. Clears the in-memory question list.
        2. Deletes questions_history.json.

        IMPORTANT:

        This method must only be called after the
        Sunday revision workflow has completed successfully.

        Normal daily generation must NOT call this method.
        """

        LOGGER.info(
            "Starting weekly history cleanup."
        )

        question_count = len(
            self.questions
        )

        # -------------------------------------------------
        # Clear in-memory history.
        # -------------------------------------------------

        self.questions.clear()

        LOGGER.info(
            "Cleared %s questions from memory.",
            question_count,
        )

        # -------------------------------------------------
        # Delete history file.
        # -------------------------------------------------

        if self.history_file.exists():

            try:

                self.history_file.unlink()

                LOGGER.info(
                    "Deleted question history file: %s",
                    self.history_file,
                )

            except OSError:

                LOGGER.exception(
                    "Failed to delete question history "
                    "file: %s",
                    self.history_file,
                )

                raise

        else:

            LOGGER.info(
                "Question history file already absent: %s",
                self.history_file,
            )

    # =====================================================
    # EXPLICIT WEEKLY CLEANUP
    # =====================================================

    def cleanup_after_review(
        self,
    ) -> None:
        """
        Clear history after successful weekly revision.

        This is an explicit alias for clear() that makes
        the intention clear when called from the Sunday
        revision workflow.
        """

        self.clear()
