"""
series_generator.py

Generates missing number series aptitude questions.
"""

from __future__ import annotations

import random
from typing import List, Tuple

from src.config import settings
from src.models.enums import (
    Difficulty,
    QuestionType,
    SeriesType,
)
from src.models.question import Question
from src.utils.constants import (
    FIBONACCI_NUMBERS,
    PERFECT_CUBES,
    PERFECT_SQUARES,
    PRIME_NUMBERS,
)
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class SeriesGenerator:
    """
    Generates missing number series questions.
    """

    def __init__(self) -> None:
        """
        Initialize series generator.
        """

        self.question_count = (
            settings.questions.series_questions
        )


    def generate(self) -> List[Question]:
        """
        Generate missing number series questions.

        Returns:
            List[Question]:
                Generated series questions.
        """

        questions: List[Question] = []

        generators = [
            self._arithmetic_series,
            self._geometric_series,
            self._fibonacci_series,
            self._square_series,
            self._cube_series,
            self._prime_series,
        ]


        while len(questions) < self.question_count:

            generator = random.choice(
                generators
            )


            sequence, answer, series_type = (
                generator()
            )


            question_text = (
                self._format_question(
                    sequence
                )
            )


            questions.append(
                Question(
                    id=len(questions) + 1,

                    question_type=(
                        QuestionType.NUMBER_SERIES
                    ),

                    difficulty=(
                        self._get_difficulty(
                            series_type
                        )
                    ),

                    question=question_text,

                    answer=str(
                        answer
                    ),

                    explanation=(
                        f"The missing number is "
                        f"{answer}"
                    ),

                    topic=(
                        "Missing Number Series"
                    ),
                )
            )


        LOGGER.info(
            "Generated %s number series questions.",
            len(questions),
        )


        return questions



    @staticmethod
    def _arithmetic_series() -> Tuple[
        List[int],
        int,
        SeriesType,
    ]:
        """
        Generate arithmetic progression.

        Returns:
            Tuple containing sequence,
            missing value and type.
        """

        start = random.randint(
            5,
            50,
        )

        difference = random.randint(
            2,
            10,
        )


        series = [
            start + (difference * index)
            for index in range(6)
        ]


        answer = series[4]

        series[4] = None


        return (
            series,
            answer,
            SeriesType.ARITHMETIC,
        )



    @staticmethod
    def _geometric_series() -> Tuple[
        List[int],
        int,
        SeriesType,
    ]:
        """
        Generate geometric progression.
        """

        start = random.randint(
            2,
            10,
        )

        ratio = random.randint(
            2,
            4,
        )


        series = [
            start * (ratio ** index)
            for index in range(6)
        ]


        answer = series[3]

        series[3] = None


        return (
            series,
            answer,
            SeriesType.GEOMETRIC,
        )



    @staticmethod
    def _fibonacci_series() -> Tuple[
        List[int],
        int,
        SeriesType,
    ]:
        """
        Generate Fibonacci sequence.
        """

        index = random.randint(
            5,
            15,
        )


        values = (
            FIBONACCI_NUMBERS[
                index - 3:index + 3
            ]
        )


        answer = values[3]

        values = list(values)

        values[3] = None


        return (
            values,
            answer,
            SeriesType.FIBONACCI,
        )



    @staticmethod
    def _square_series() -> Tuple[
        List[int],
        int,
        SeriesType,
    ]:
        """
        Generate square number series.
        """

        values = list(
            PERFECT_SQUARES.keys()
        )


        start = random.randint(
            0,
            len(values) - 6,
        )


        series = values[
            start:start + 6
        ]


        answer = series[2]

        series[2] = None


        return (
            series,
            answer,
            SeriesType.SQUARES,
        )



    @staticmethod
    def _cube_series() -> Tuple[
        List[int],
        int,
        SeriesType,
    ]:
        """
        Generate cube number series.
        """

        values = list(
            PERFECT_CUBES.keys()
        )


        start = random.randint(
            0,
            len(values) - 6,
        )


        series = values[
            start:start + 6
        ]


        answer = series[2]

        series[2] = None


        return (
            series,
            answer,
            SeriesType.CUBES,
        )



    @staticmethod
    def _prime_series() -> Tuple[
        List[int],
        int,
        SeriesType,
    ]:
        """
        Generate prime number series.
        """

        start = random.randint(
            0,
            len(PRIME_NUMBERS) - 6,
        )


        series = PRIME_NUMBERS[
            start:start + 6
        ]


        answer = series[4]

        series[4] = None


        return (
            series,
            answer,
            SeriesType.PRIMES,
        )



    @staticmethod
    def _format_question(
        sequence: List[int | None],
    ) -> str:
        """
        Convert sequence into question text.

        Args:
            sequence:
                Number sequence.

        Returns:
            str:
                Formatted question.
        """

        formatted = ", ".join(
            "?"
            if value is None
            else str(value)
            for value in sequence
        )


        return (
            f"Find the missing number: "
            f"{formatted}"
        )



    @staticmethod
    def _get_difficulty(
        series_type: SeriesType,
    ) -> Difficulty:
        """
        Determine difficulty.

        Args:
            series_type:
                Series category.

        Returns:
            Difficulty:
                Difficulty category.
        """

        if series_type in (
            SeriesType.ARITHMETIC,
            SeriesType.SQUARES,
        ):

            return Difficulty.EASY


        if series_type in (
            SeriesType.GEOMETRIC,
            SeriesType.CUBES,
        ):

            return Difficulty.MEDIUM


        return Difficulty.HARD