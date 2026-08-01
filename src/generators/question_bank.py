"""
question_bank.py

Central question collection service for the
Daily Aptitude Generator.

Combines all individual question generators
into a single question generation entry point.
"""

from __future__ import annotations

from typing import List

from src.generators.cube_generator import CubeGenerator
from src.generators.cube_root_generator import CubeRootGenerator
from src.generators.series_generator import SeriesGenerator
from src.generators.simplification_generator import (
    SimplificationGenerator,
)
from src.generators.square_generator import SquareGenerator
from src.generators.square_root_generator import (
    SquareRootGenerator,
)
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class QuestionBank:
    """
    Manages all aptitude question generators.

    This class acts as a single entry point
    for generating the complete question pool.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize all question generators.

        The order below determines the order
        of questions in the generated pool.
        """

        self.generators = [
            SquareGenerator(),
            CubeGenerator(),
            SquareRootGenerator(),
            CubeRootGenerator(),
            SimplificationGenerator(),
            SeriesGenerator(),
        ]


    def generate(
        self,
    ) -> List[Question]:
        """
        Generate complete aptitude question pool.

        Returns:
            List[Question]:
                Combined list of questions
                from all categories.
        """

        questions: List[
            Question
        ] = []


        for generator in self.generators:

            generated_questions = (
                generator.generate()
            )

            questions.extend(
                generated_questions
            )


        self._reassign_ids(
            questions
        )


        LOGGER.info(
            "Total questions generated: %s",
            len(questions),
        )


        return questions


    @staticmethod
    def _reassign_ids(
        questions: List[
            Question
        ],
    ) -> None:
        """
        Assign sequential IDs after combining
        questions from all generators.

        Args:
            questions:
                Combined question list.
        """

        for index, question in enumerate(
            questions,
            start=1,
        ):

            question.id = index