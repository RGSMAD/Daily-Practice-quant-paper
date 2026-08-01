"""
simplification_generator.py

Generates banking aptitude simplification questions.

Patterns:
- BODMAS simplification
- Missing value
- Percentage approximation
- Decimal simplification
- Fraction based simplification
- Square based simplification
- Approximation
"""

from __future__ import annotations

import random
from fractions import Fraction
from typing import List, Tuple, Callable

from src.config import settings
from src.models.enums import Difficulty, QuestionType
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class SimplificationGenerator:
    """
    Generates simplification aptitude questions.
    """


    def __init__(self) -> None:

        self.question_count = (
            settings.questions.simplification_questions
        )

        self.minimum = (
            settings.ranges.simplification_min_operand
        )

        self.maximum = (
            settings.ranges.simplification_max_operand
        )

        self.generated: set[str] = set()



    # =========================================================
    # MAIN GENERATOR
    # =========================================================

    def generate(self) -> List[Question]:

        questions: List[Question] = []


        generators: List[Tuple[Callable, int]] = [

            (self._generate_bodmas, 5),

            (self._generate_missing_value, 4),

            (self._generate_percentage, 4),

            (self._generate_decimal, 3),

            (self._generate_fraction, 2),

            (self._generate_approximation, 2),

        ]


        for generator, count in generators:

            for _ in range(count):

                questions.append(
                    self._create_question(
                        generator()
                    )
                )


        random.shuffle(
            questions
        )


        questions = questions[
            : self.question_count
        ]


        LOGGER.info(
            "Generated %s simplification questions.",
            len(questions),
        )


        return questions



    # =========================================================
    # BUILDER
    # =========================================================

    def _create_question(
        self,
        data: Tuple[str, str, Difficulty],
    ) -> Question:

        question, answer, difficulty = data


        return Question(

            id=0,

            question_type=(
                QuestionType.SIMPLIFICATION
            ),

            difficulty=difficulty,

            question=question,

            answer=str(answer),

            explanation=(
                f"{question} = {answer}"
            ),

            topic="Simplification",
        )



    # =========================================================
    # BODMAS
    # =========================================================

    def _generate_bodmas(
        self,
    ) -> Tuple[str, str, Difficulty]:

        a = random.randint(10, 100)
        b = random.randint(5, 50)
        c = random.randint(2, 20)
        d = random.randint(2, 15)


        patterns = [

            (
                f"{a} + {b} × {c} - {d}",
                a + (b * c) - d,
            ),

            (
                f"({a} + {b}) × {c} - {d}",
                (a + b) * c - d,
            ),

            (
                f"{a} × {b} ÷ {c} + {d}",
                (a * b) // c + d,
            ),

        ]


        expression, answer = random.choice(
            patterns
        )


        return (

            f"{expression} = ?",

            str(answer),

            Difficulty.MEDIUM,

        )



    # =========================================================
    # MISSING VALUE
    # =========================================================

    def _generate_missing_value(
        self,
    ) -> Tuple[str, str, Difficulty]:


        value = random.randint(
            20,
            200,
        )


        multiplier = random.randint(
            2,
            20,
        )


        total = value * multiplier


        return (

            f"({value} × {multiplier}) - ? = {total - value}",

            str(value),

            Difficulty.HARD,

        )



    # =========================================================
    # PERCENTAGE
    # =========================================================

    def _generate_percentage(
        self,
    ) -> Tuple[str, str, Difficulty]:


        percent = random.choice(
            [
                9.99,
                19.98,
                39.98,
                49.98,
                50.02,
            ]
        )


        number = random.choice(
            [
                498,
                502,
                998,
                1002,
            ]
        )


        answer = round(
            percent * number / 100
        )


        return (

            f"{percent}% of {number} = ?",

            str(answer),

            Difficulty.HARD,

        )



    # =========================================================
    # DECIMAL
    # =========================================================

    def _generate_decimal(
        self,
    ) -> Tuple[str, str, Difficulty]:


        numbers = [
            round(
                random.uniform(10, 99),
                1
            )
            for _ in range(5)
        ]


        answer = round(
            sum(numbers),
            1
        )


        expression = (
            " + ".join(
                str(x)
                for x in numbers
            )
        )


        return (

            f"{expression} = ?",

            str(answer),

            Difficulty.MEDIUM,

        )



    # =========================================================
    # FRACTION
    # =========================================================

    def _generate_fraction(
        self,
    ) -> Tuple[str, str, Difficulty]:


        number = random.choice(
            [
                200,
                300,
                400,
                500,
            ]
        )


        fraction = random.choice(
            [
                "1/2",
                "1/4",
                "2/5",
                "3/5",
            ]
        )


        result = (
            Fraction(fraction)
            *
            number
        )


        return (

            f"{fraction} of {number} = ?",

            str(int(result)),

            Difficulty.MEDIUM,

        )



    # =========================================================
    # APPROXIMATION
    # =========================================================

    def _generate_approximation(
        self,
    ) -> Tuple[str, str, Difficulty]:


        patterns = [

            (
                "12.2 + 12.6 + 12.8 + 12.3 + 12.1",
                62,
            ),

            (
                "49.8 × 20",
                996,
            ),

            (
                "39.98% of 1002",
                401,
            ),

        ]


        expression, answer = random.choice(
            patterns
        )


        return (

            f"{expression} ≈ ?",

            str(answer),

            Difficulty.HARD,

        )