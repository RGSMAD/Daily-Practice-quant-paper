"""
test_utils.py

Tests for utility modules.
"""

from __future__ import annotations

import logging

from pathlib import Path

import pytest

from src.models.enums import (
    Difficulty,
    QuestionType,
)
from src.models.question import Question
from src.utils.helpers import (
    ensure_directory,
)
from src.utils.history import (
    HistoryManager,
)
from src.utils.logger import (
    get_logger,
)
from src.utils.validator import (
    validate_file_exists,
)



def test_ensure_directory(
    tmp_path: Path,
) -> None:
    """
    Test directory creation helper.
    """

    new_directory = (
        tmp_path
        / "test_folder"
    )


    result = (
        ensure_directory(
            new_directory
        )
    )


    assert result.exists()

    assert result.is_dir()



def test_validate_existing_file(
    tmp_path: Path,
) -> None:
    """
    Test file validation success.
    """

    file_path = (
        tmp_path
        / "sample.txt"
    )


    file_path.write_text(
        "test data",
        encoding="utf-8",
    )


    result = (
        validate_file_exists(
            file_path
        )
    )


    assert result is True



def test_validate_missing_file(
    tmp_path: Path,
) -> None:
    """
    Test validation failure
    for missing file.
    """

    missing_file = (
        tmp_path
        / "missing.txt"
    )


    with pytest.raises(
        FileNotFoundError
    ):

        validate_file_exists(
            missing_file
        )



def test_logger_creation() -> None:
    """
    Test logger creation.
    """

    logger = (
        get_logger(
            "test_logger"
        )
    )


    assert isinstance(
        logger,
        logging.Logger,
    )



def test_history_add_and_check(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """
    Test history duplicate detection.
    """

    history_file = (
        tmp_path
        / "history.json"
    )


    monkeypatch.setattr(
        "src.utils.history.settings.paths.history_dir",
        tmp_path,
    )


    question = Question(
        id=1,
        question_type=(
            QuestionType.SQUARE
        ),
        difficulty=(
            Difficulty.EASY
        ),
        question=(
            "What is the square of 10?"
        ),
        answer="100",
        topic="Squares",
    )


    manager = (
        HistoryManager()
    )


    manager.add_questions(
        [question]
    )


    assert manager.exists(
        question.question
    )



def test_history_save_and_load(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """
    Test history persistence.
    """

    monkeypatch.setattr(
        "src.utils.history.settings.paths.history_dir",
        tmp_path,
    )


    question = Question(
        id=1,
        question_type=(
            QuestionType.CUBE
        ),
        difficulty=(
            Difficulty.EASY
        ),
        question=(
            "What is cube of 5?"
        ),
        answer="125",
        topic="Cubes",
    )


    manager = (
        HistoryManager()
    )


    manager.add_questions(
        [question]
    )


    manager.save()


    new_manager = (
        HistoryManager()
    )


    new_manager.load()


    assert new_manager.exists(
        question.question
    )