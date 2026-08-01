"""
test_pdf.py

Tests for PDF generation modules.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.models.answer import Answer
from src.models.enums import (
    Difficulty,
    QuestionType,
)
from src.models.question import Question
from src.pdf.answer_pdf import AnswerPDFGenerator
from src.pdf.question_pdf import (
    QuestionPDFGenerator,
)



@pytest.fixture
def sample_questions() -> list[Question]:
    """
    Provide sample questions for PDF testing.

    Returns:
        list[Question]:
            Sample question objects.
    """

    return [
        Question(
            id=1,
            question_type=QuestionType.SQUARE,
            difficulty=Difficulty.EASY,
            question="What is the square of 25?",
            answer="625",
            explanation="25 × 25 = 625",
            topic="Squares",
        ),
        Question(
            id=2,
            question_type=QuestionType.CUBE,
            difficulty=Difficulty.MEDIUM,
            question="What is the cube of 5?",
            answer="125",
            explanation="5 × 5 × 5 = 125",
            topic="Cubes",
        ),
    ]



@pytest.fixture
def sample_answers() -> list[Answer]:
    """
    Provide sample answers for PDF testing.

    Returns:
        list[Answer]:
            Sample answer objects.
    """

    return [
        Answer(
            question_id=1,
            answer="625",
        ),
        Answer(
            question_id=2,
            answer="125",
        ),
    ]



def test_question_pdf_creation(
    tmp_path: Path,
    sample_questions: list[Question],
) -> None:
    """
    Test question PDF generation.

    Args:
        tmp_path:
            Temporary test directory.

        sample_questions:
            Sample questions.
    """

    output_file = (
        tmp_path
        / "questions.pdf"
    )


    generator = (
        QuestionPDFGenerator()
    )


    generated_file = (
        generator.generate(
            sample_questions,
            output_file,
        )
    )


    assert generated_file.exists()

    assert generated_file.suffix == ".pdf"



def test_answer_pdf_creation(
    tmp_path: Path,
    sample_answers: list[Answer],
) -> None:
    """
    Test answer PDF generation.

    Args:
        tmp_path:
            Temporary test directory.

        sample_answers:
            Sample answers.
    """

    output_file = (
        tmp_path
        / "answers.pdf"
    )


    generator = (
        AnswerPDFGenerator()
    )


    generated_file = (
        generator.generate(
            sample_answers,
            output_file,
        )
    )


    assert generated_file.exists()

    assert generated_file.suffix == ".pdf"



def test_pdf_file_is_not_empty(
    tmp_path: Path,
    sample_questions: list[Question],
) -> None:
    """
    Ensure generated PDF contains data.
    """

    output_file = (
        tmp_path
        / "validation.pdf"
    )


    QuestionPDFGenerator().generate(
        sample_questions,
        output_file,
    )


    assert output_file.stat().st_size > 0