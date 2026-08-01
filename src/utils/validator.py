"""Validation utilities for the Daily Aptitude Generator.

This module provides reusable validation functions for configuration,
generated questions, file paths, and application inputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from src.models.question import Question


def validate_positive_integer(
    value: int,
    field_name: str,
) -> None:
    """Validate that an integer is positive.

    Args:
        value:
            Integer value to validate.

        field_name:
            Name of the field being validated.

    Raises:
        ValueError:
            If the value is not a positive integer.
    """
    if value <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )


def validate_non_negative_integer(
    value: int,
    field_name: str,
) -> None:
    """Validate that an integer is non-negative.

    Args:
        value:
            Integer value.

        field_name:
            Field name.

    Raises:
        ValueError:
            If the value is negative.
    """
    if value < 0:
        raise ValueError(
            f"{field_name} cannot be negative."
        )


def validate_not_empty(
    value: str,
    field_name: str,
) -> None:
    """Validate that a string is not empty.

    Args:
        value:
            String value.

        field_name:
            Name of the field.

    Raises:
        ValueError:
            If the string is empty.
    """
    if not value or not value.strip():
        raise ValueError(
            f"{field_name} cannot be empty."
        )


def validate_file_exists(
    file_path: str | Path,
) -> None:
    """Validate that a file exists.

    Args:
        file_path:
            File path.

    Raises:
        FileNotFoundError:
            If the file does not exist.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"File not found: {path}"
        )


def validate_directory_exists(
    directory: str | Path,
) -> None:
    """Validate that a directory exists.

    Args:
        directory:
            Directory path.

    Raises:
        FileNotFoundError:
            If the directory does not exist.
    """
    path = Path(directory)

    if not path.is_dir():
        raise FileNotFoundError(
            f"Directory not found: {path}"
        )


def validate_questions(
    questions: Iterable[Question],
) -> None:
    """Validate generated questions.

    Args:
        questions:
            Collection of Question objects.

    Raises:
        ValueError:
            If any question contains invalid data.
    """
    question_list = list(questions)

    if not question_list:
        raise ValueError(
            "Question list cannot be empty."
        )

    seen_questions: set[str] = set()

    for index, question in enumerate(
        question_list,
        start=1,
    ):
        if not question.question.strip():
            raise ValueError(
                f"Question {index} has empty text."
            )

        if not question.answer.value.strip():
            raise ValueError(
                f"Question {index} has an empty answer."
            )

        if question.question in seen_questions:
            raise ValueError(
                f"Duplicate question detected: "
                f"{question.question}"
            )

        seen_questions.add(question.question)


def validate_output_path(
    output_path: str | Path,
) -> None:
    """Validate an output file path.

    Args:
        output_path:
            Output file path.

    Raises:
        ValueError:
            If the output path is invalid.
    """
    path = Path(output_path)

    if not path.suffix:
        raise ValueError(
            "Output file must contain an extension."
        )

    if path.name.strip() == "":
        raise ValueError(
            "Invalid output filename."
        )


def validate_email_address(
    email: str,
) -> None:
    """Validate an email address.

    Args:
        email:
            Email address.

    Raises:
        ValueError:
            If the email address is invalid.
    """
    validate_not_empty(
        email,
        "Email address",
    )

    if "@" not in email or "." not in email:
        raise ValueError(
            f"Invalid email address: {email}"
        )


def validate_question_count(
    count: int,
) -> None:
    """Validate requested question count.

    Args:
        count:
            Number of questions.

    Raises:
        ValueError:
            If the count is invalid.
    """
    validate_positive_integer(
        count,
        "Question count",
    )