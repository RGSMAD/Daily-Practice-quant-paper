"""
test_generators.py

Tests for aptitude question generators.
"""

from __future__ import annotations

import pytest

from src.config import settings
from src.generators.cube_generator import CubeGenerator
from src.generators.cube_root_generator import (
    CubeRootGenerator,
)
from src.generators.question_bank import QuestionBank
from src.generators.series_generator import (
    SeriesGenerator,
)
from src.generators.simplification_generator import (
    SimplificationGenerator,
)
from src.generators.square_generator import (
    SquareGenerator,
)
from src.generators.square_root_generator import (
    SquareRootGenerator,
)
from src.models.enums import QuestionType
from src.models.question import Question



@pytest.mark.parametrize(
    "generator, expected_count, question_type",
    [
        (
            SquareGenerator(),
            settings.questions.square_questions,
            QuestionType.SQUARE,
        ),
        (
            CubeGenerator(),
            settings.questions.cube_questions,
            QuestionType.CUBE,
        ),
        (
            SquareRootGenerator(),
            settings.questions.square_root_questions,
            QuestionType.SQUARE_ROOT,
        ),
        (
            CubeRootGenerator(),
            settings.questions.cube_root_questions,
            QuestionType.CUBE_ROOT,
        ),
        (
            SimplificationGenerator(),
            settings.questions.simplification_questions,
            QuestionType.SIMPLIFICATION,
        ),
        (
            SeriesGenerator(),
            settings.questions.series_questions,
            QuestionType.NUMBER_SERIES,
        ),
    ],
)
def test_generator_output(
    generator,
    expected_count: int,
    question_type: QuestionType,
) -> None:
    """
    Validate individual generators.

    Args:
        generator:
            Generator instance.

        expected_count:
            Expected generated questions.

        question_type:
            Expected question category.
    """

    questions = (
        generator.generate()
    )


    assert len(questions) == expected_count


    for question in questions:

        assert isinstance(
            question,
            Question,
        )


        assert (
            question.question_type
            == question_type
        )


        assert question.question

        assert question.answer



def test_question_bank_generation() -> None:
    """
    Test combined question bank generation.
    """

    question_bank = (
        QuestionBank()
    )


    questions = (
        question_bank.generate()
    )


    expected_total = (
        settings.questions.square_questions
        + settings.questions.cube_questions
        + settings.questions.square_root_questions
        + settings.questions.cube_root_questions
        + settings.questions.simplification_questions
        + settings.questions.series_questions
    )


    assert len(questions) == expected_total



def test_question_ids_are_unique() -> None:
    """
    Ensure question IDs are unique.
    """

    questions = (
        QuestionBank()
        .generate()
    )


    ids = [
        question.id
        for question in questions
    ]


    assert len(ids) == len(set(ids))