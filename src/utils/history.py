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
        | Generate weekly review paper
        | Successfully complete paper generation
        v
    Cleanup active history
        |
        +--> Clear in-memory questions
        |
        +--> Remove active.json

Important:
    Normal save() NEVER performs cleanup.

History is cleaned only through an explicit
cleanup_after_review() call after the weekly
review has been successfully generated.
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
    question history used for duplicate detection.

    History is intentionally preserved during normal
    daily generation and is cleared only after the
    weekly review has been successfully generated.
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
            cleanup.

        Daily generation must be able to preserve all
        questions generated during the current week.

        Cleanup happens explicitly through
        cleanup_after_review() after the weekly review
        has been successfully generated.
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
    # WEEKLY HISTORY
    # =========================================================

    def weekly_questions(self) -> list[Question]:
        """
        Return the questions retained for the
        current weekly review.

        The weekly review is based on the active
        history accumulated before the review day.

        Returns:
            All active weekly questions ordered by
            creation time.
        """

        return sorted(
            self.questions,
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

        This is optional and controlled by the
        archive_monthly configuration.

        The active history itself is NOT removed here.

        Returns:
            Path to the archive file if archived,
            otherwise None.
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
        Clear active history after the weekly review
        has been successfully generated.

        IMPORTANT:
            This method should only be called AFTER
            the weekly review question/answer paper
            has been successfully generated.

        Args:
            archive:
                If True, archive the current history
                before clearing it.

        The cleanup performs both operations:

            1. Clear in-memory HistoryManager state.
            2. Delete the active history file.

        This prevents old weekly questions from affecting
        the next week's duplicate detection.
        """

        if not self.settings.enabled:

            self.questions.clear()

            return

        LOGGER.info(
            "Starting post-review history cleanup."
        )

        if archive:

            self.archive_current_history()

        # -----------------------------------------------------
        # Clear in-memory history first.
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
        # Delete active history file.
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
    # BACKWARD-COMPATIBLE CLEANUP NAME
    # =========================================================

    def cleanup(
        self,
    ) -> None:
        """
        Explicitly clean active history.

        This method is retained as a convenient public
        cleanup entry point.

        It does NOT run automatically during save().

        For weekly review workflows, prefer:

            cleanup_after_review()

        after successful review generation.
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
```
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
