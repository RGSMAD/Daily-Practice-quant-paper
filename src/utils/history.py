"""
history.py

Basic question history management for the
Daily Aptitude Generator.

Revision 1:
- Load history
- Save history
- Add questions
- Basic duplicate detection
"""

import json

from __future__ import annotations

from pathlib import Path

from models.question import Question
from utils.config import settings


# ============================================================
# HISTORY PATH
# ============================================================

def get_history_file() -> Path:
    """
    Return history file path.

    Creates history directory if it does not exist.
    """

    history_dir = settings.paths.history_dir

    history_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return history_dir / settings.history.filename


# ============================================================
# LOAD HISTORY
# ============================================================

def load_history() -> list[Question]:
    """
    Load stored questions from history file.

    Returns:
        List of Question objects.

    If history file does not exist,
    returns an empty list.
    """

    file_path = get_history_file()

    if not file_path.exists():
        return []

    try:
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

    except json.JSONDecodeError:
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
    Save questions into history file.
    """

    file_path = get_history_file()

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            [
                question.to_dict()
                for question in questions
            ],
            file,
            indent=4,
            ensure_ascii=False,
        )


# ============================================================
# DUPLICATE CHECK
# ============================================================

def is_duplicate(
    question: Question,
    history: list[Question],
) -> bool:
    """
    Check whether question already exists.
    """

    return any(
        existing.fingerprint
        == question.fingerprint
        for existing in history
    )


# ============================================================
# ADD QUESTION
# ============================================================

def add_question(
    question: Question,
) -> bool:
    """
    Add a question to history.

    Returns:
        True:
            Question added successfully.

        False:
            Duplicate question found.
    """

    history = load_history()

    if is_duplicate(
        question,
        history,
    ):
        return False

    history.append(
        question
    )

    save_history(
        history
    )

    return True

"""
history.py

Question history management for the
Daily Aptitude Generator.

Revision 2:
- Load history
- Save history
- Add questions
- Duplicate detection
- Retention cleanup
- Maximum record control
- History utilities
"""

from __future__ import annotations

import json

from datetime import datetime, timedelta
from pathlib import Path

from models.question import Question
from utils.config import settings


# ============================================================
# HISTORY PATH
# ============================================================

def get_history_file() -> Path:
    """
    Return history file path.

    Creates history directory automatically.
    """

    history_dir = settings.paths.history_dir

    history_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return history_dir / settings.history.filename


# ============================================================
# HISTORY STATUS
# ============================================================

def is_history_enabled() -> bool:
    """
    Check whether history tracking is enabled.
    """

    return settings.history.enabled


# ============================================================
# LOAD HISTORY
# ============================================================

def load_history() -> list[Question]:
    """
    Load questions from history file.
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
    Save questions after cleanup.
    """

    if not is_history_enabled():
        return

    questions = cleanup_history(
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
                for question in questions
            ],
            file,
            indent=4,
            ensure_ascii=False,
        )


# ============================================================
# DUPLICATE CHECK
# ============================================================

def is_duplicate(
    question: Question,
    history: list[Question],
) -> bool:
    """
    Check duplicate question using fingerprint.
    """

    return any(
        item.fingerprint
        == question.fingerprint
        for item in history
    )


# ============================================================
# ADD QUESTION
# ============================================================

def add_question(
    question: Question,
) -> bool:
    """
    Add question to history.

    Returns:
        True  -> Added
        False -> Duplicate
    """

    if not is_history_enabled():
        return True

    history = load_history()

    if is_duplicate(
        question,
        history,
    ):
        return False

    history.append(
        question
    )

    save_history(
        history
    )

    return True


# ============================================================
# CLEANUP
# ============================================================

def cleanup_history(
    questions: list[Question],
) -> list[Question]:
    """
    Remove expired records and
    maintain maximum history size.
    """

    expiry_date = (
        datetime.now()
        -
        timedelta(
            days=settings.history.retain_days
        )
    )

    filtered_questions = [
        question
        for question in questions
        if question.created_at >= expiry_date
    ]


    return filtered_questions[
        -settings.history.max_records:
    ]


# ============================================================
# RECENT QUESTIONS
# ============================================================

def get_recent_questions(
    days: int = 7,
) -> list[Question]:
    """
    Return questions generated within
    specified number of days.
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
    Remove complete history file.
    """

    file_path = get_history_file()

    if file_path.exists():
        file_path.unlink()
