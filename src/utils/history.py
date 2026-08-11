
"""
history.py

Question history management for the
Daily Aptitude Generator.

History lifecycle:

    Monday - Saturday
        |
        | Generate daily questions
        | Add questions to active history
        | Save active history
        v
    active.json
        |
        | Sunday
        | Read six days of history
        | Generate weekly revision paper
        | Successfully complete revision
        v
    Cleanup active history
        |
        +--> Clear in-memory questions
        |
        +--> Remove active.json

Important:

    Normal save() NEVER performs cleanup.

    History is cleaned only through the explicit
    cleanup_after_review() call after the weekly
    revision has been successfully generated.
"""

from __future__ import annotations

import json
import shutil

from datetime import datetime, timedelta
from pathlib import Path

from src.config import settings
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class HistoryManager:
    """
    Manages generated question history.

    The history manager maintains the active weekly
    question history used for:

        - Duplicate detection
        - Sunday revision generation

    History is intentionally preserved during normal
    daily generation and is cleared only after the
    Sunday revision has been successfully generated.
    """

    # =========================================================
    # INITIALIZATION
    # =========================================================

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

        self.archive_directory: Path = (
            self.history_directory
            / self.settings.archive_directory
        )

        self.questions: list[Question] = []

        self.history_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.load()

    # =========================================================
    # LOAD
    # =========================================================

    def load(self) -> None:
        """
        Load active history from disk.

        If history is disabled or the active history
        file does not exist, the in-memory history is
        initialized as an empty list.
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
                "No active history file found: %s",
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
                "Failed to load history from %s.",
                self.history_file,
            )

            self.questions = []

    # =========================================================
    # SAVE
    # =========================================================

    def save(self) -> None:
        """
        Save current active history to disk.

        IMPORTANT:

            This method intentionally does NOT perform
            any cleanup.

        Daily generation must preserve all questions
        generated during the current week.

        Cleanup happens explicitly through:

            cleanup_after_review()

        after successful Sunday revision generation.
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
                "Saved %s questions to history.",
                len(self.questions),
            )

        except OSError:

            LOGGER.exception(
                "Failed to save history to %s.",
                self.history_file,
            )

            raise

    # =========================================================
    # DUPLICATE CHECK
    # =========================================================

    def is_duplicate(
        self,
        question: Question,
    ) -> bool:
        """
        Check whether a question already exists
        in active history.

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

    # =========================================================
    # ADD SINGLE QUESTION
    # =========================================================

    def add_question(
        self,
        question: Question,
    ) -> bool:
        """
        Add one question to active history.

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
                "Duplicate question rejected by history: %s",
                question.question,
            )

            return False

        self.questions.append(question)

        return True

    # =========================================================
    # ADD MULTIPLE QUESTIONS
    # =========================================================

    def add_questions(
        self,
        questions: list[Question],
    ) -> None:
        """
        Add multiple questions to active history.

        Duplicate questions are silently skipped.
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

    # =========================================================
    # RECENT QUESTIONS
    # =========================================================

    def recent(
        self,
        days: int = 7,
    ) -> list[Question]:
        """
        Return questions generated within the
        specified number of days.

        Args:
            days:
                Number of days to look back.

        Returns:
            List of recent questions.
        """

        if days <= 0:

            return []

        cutoff = (
            datetime.now()
            - timedelta(days=days)
        )

        return [
            question
            for question in self.questions
            if question.created_at >= cutoff
        ]

    # =========================================================
    # WEEKLY QUESTIONS
    # =========================================================

    def weekly_questions(self) -> list[Question]:
        """
        Return all active questions intended for
        the current Sunday revision.

        The questions are ordered by creation time.

        Monday-Saturday questions are therefore returned
        in chronological order for revision processing.
        """

        return sorted(
            self.questions,
            key=lambda question: question.created_at,
        )

    # =========================================================
    # QUESTIONS BY TOPIC
    # =========================================================

    def questions_by_topic(
        self,
        topic: str,
    ) -> list[Question]:
        """
        Return all active questions belonging to
        the specified topic.

        Args:
            topic:
                Topic name, for example:
                "Squares", "Cubes", etc.

        Returns:
            Matching questions ordered by creation time.
        """

        return sorted(
            [
                question
                for question in self.questions
                if question.topic == topic
            ],
            key=lambda question: question.created_at,
        )

    # =========================================================
    # COUNT
    # =========================================================

    def count(self) -> int:
        """
        Return the number of questions currently
        stored in active history.
        """

        return len(self.questions)

    # =========================================================
    # ARCHIVE
    # =========================================================

    def archive_current_history(self) -> Path | None:
        """
        Archive the current active history.

        Archiving is controlled by the
        archive_monthly configuration.

        The active history itself is NOT removed here.

        Returns:
            Path:
                Archive file path if archived.

            None:
                If archiving is disabled or no history
                file exists.
        """

        if not self.settings.enabled:

            return None

        if not self.settings.archive_monthly:

            return None

        if not self.history_file.exists():

            LOGGER.info(
                "No active history available for archiving."
            )

            return None

        self.archive_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        archive_file = (
            self.archive_directory
            / f"history_{timestamp}.json"
        )

        try:

            shutil.copy2(
                self.history_file,
                archive_file,
            )

            LOGGER.info(
                "Archived active history to %s.",
                archive_file,
            )

            return archive_file

        except OSError:

            LOGGER.exception(
                "Failed to archive history."
            )

            raise

    # =========================================================
    # WEEKLY CLEANUP
    # =========================================================

    def cleanup_after_review(
        self,
        archive: bool = False,
    ) -> None:
        """
        Clear active history after the Sunday revision
        has been successfully generated.

        IMPORTANT:

            This method must only be called after:

                1. Revision questions were successfully
                   selected.
                2. Question PDF was successfully generated.
                3. Answer PDF was successfully generated.

        Args:
            archive:
                If True, archive the current history
                before clearing it.

        Cleanup performs:

            1. Optional archive
            2. Clear in-memory history
            3. Delete active.json

        This ensures that the next Monday starts
        with an empty weekly history.
        """

        if not self.settings.enabled:

            self.questions.clear()

            return

        LOGGER.info(
            "Starting post-review history cleanup."
        )

        # -----------------------------------------------------
        # Optional archive
        # -----------------------------------------------------

        if archive:

            self.archive_current_history()

        # -----------------------------------------------------
        # Clear in-memory history
        # -----------------------------------------------------

        question_count = len(
            self.questions
        )

        self.questions.clear()

        LOGGER.info(
            "Cleared %s questions from HistoryManager.",
            question_count,
        )

        # -----------------------------------------------------
        # Delete active history file
        # -----------------------------------------------------

        if self.history_file.exists():

            try:

                self.history_file.unlink()

                LOGGER.info(
                    "Deleted active history file: %s",
                    self.history_file,
                )

            except OSError:

                LOGGER.exception(
                    "Failed to delete active history file: %s",
                    self.history_file,
                )

                raise

        else:

            LOGGER.info(
                "Active history file already absent."
            )

    # =========================================================
    # BACKWARD-COMPATIBLE CLEANUP
    # =========================================================

    def cleanup(self) -> None:
        """
        Explicitly clean active history.

        This method does NOT run automatically during
        save().

        For the Sunday revision workflow, prefer:

            cleanup_after_review()
        """

        self.cleanup_after_review()

    # =========================================================
    # CLEAR
    # =========================================================

    def clear(self) -> None:
        """
        Completely clear active history.

        This is an explicit operation and should not
        be called during normal daily generation.
        """

        self.questions.clear()

        if self.history_file.exists():

            try:

                self.history_file.unlink()

            except OSError:

                LOGGER.exception(
                    "Failed to delete history file: %s",
                    self.history_file,
                )

                raise

        LOGGER.info(
            "Active question history cleared."
        )
