"""
history.py

Question history management for the
Daily Aptitude Generator.

Responsible for:
- Loading history
- Saving history
- Duplicate detection
- History cleanup
- Recent question retrieval
"""

from __future__ import annotations

import json

from datetime import datetime, timedelta
from pathlib import Path

from src.config import settings
from src.models.question import Question


# ============================================================
# HISTORY PATH
# ============================================================

def get_history_file() -> Path:
    """
    Return history file path.

    Creates history directory if necessary.
    """

    history_dir = settings.paths.history_dir

    history_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        history_dir
        / settings.history.filename
    )


# ============================================================
# HISTORY STATUS
# ============================================================

def is_history_enabled() -> bool:
    """
    Check whether history tracking
    is enabled.
    """

    return settings.history.enabled


# ============================================================
# LOAD HISTORY
# ============================================================

def load_history() -> list[Question]:
    """
    Load question history from disk.
    """

    if not is_history_enabled():
        return []

    file_path = get_history_file()

    if not file_path.exists():
        return []

    try:

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return []

    return [
        Question.from_dict(item)
        for item in data
    ]


# ============================================================
# SAVE HISTORY
# ============================================================

def save_history(
    questions: list[Question],
) -> None:
    """
    Save history after cleanup.
    """

    if not is_history_enabled():
        return

    cleaned = cleanup_history(
        questions
    )

    file_path = get_history_file()

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            [
                question.to_dict()
                for question in cleaned
            ],
            file,
            indent=4,
            ensure_ascii=False,
        )


# ============================================================
# CLEANUP
# ============================================================

def cleanup_history(
    questions: list[Question],
) -> list[Question]:
    """
    Remove expired history and
    enforce maximum record limit.
    """

    expiry = (
        datetime.now()
        -
        timedelta(
            days=settings.history.retain_days
        )
    )

    filtered = [
        question
        for question in questions
        if question.created_at >= expiry
    ]

    return filtered[
        -settings.history.max_records:
    ]


# ============================================================
# RECENT QUESTIONS
# ============================================================

def get_recent_questions(
    days: int = 7,
) -> list[Question]:
    """
    Return recently generated questions.
    """

    cutoff = (
        datetime.now()
        -
        timedelta(days=days)
    )

    return [
        question
        for question in load_history()
        if question.created_at >= cutoff
    ]


# ============================================================
# CLEAR HISTORY
# ============================================================

def clear_history() -> None:
    """
    Delete history file.
    """

    file_path = get_history_file()

    if file_path.exists():

        file_path.unlink()


# ============================================================
# HISTORY MANAGER
# ============================================================

class HistoryManager:
    """
    Manages question history.
    """

    def __init__(
        self,
    ) -> None:

        self._history = (
            load_history()
        )


    def exists(
        self,
        question: Question,
    ) -> bool:
        """
        Check whether question
        already exists.
        """

        return any(
            item.fingerprint
            == question.fingerprint
            for item in self._history
        )


    def add_question(
        self,
        question: Question,
    ) -> bool:
        """
        Add one question.

        Returns:
            True if added.
            False if duplicate.
        """

        if self.exists(
            question
        ):
            return False

        self._history.append(
            question
        )

        return True


    def add_questions(
        self,
        questions: list[Question],
    ) -> None:
        """
        Add multiple questions.
        """

        for question in questions:

            self.add_question(
                question
            )


    def load(
        self,
    ) -> list[Question]:
        """
        Return loaded history.
        """

        return list(
            self._history
        )


    def save(
        self,
    ) -> None:
        """
        Persist history.
        """

        save_history(
            self._history
        )


    def recent(
        self,
        days: int = 7,
    ) -> list[Question]:
        """
        Return recent questions.
        """

        return get_recent_questions(
            days
        )


    def clear(
        self,
    ) -> None:
        """
        Clear history.
        """

        self._history.clear()

        clear_history()