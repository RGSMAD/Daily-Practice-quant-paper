"""
simplification_generator.py

Generates banking aptitude simplification questions.

Patterns:
- BODMAS
- Missing value
- Decimal simplification
- Percentage approximation
- Fraction simplification
- Difference of squares
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


    # =========================================================
    # MAIN
    # =========================================================

    def generate(self) -> List[Question]:

        questions: List[Question] = []


        generators: List[Tuple[Callable, int]] = [

            (self._generate_bodmas, 4),

            (self._generate_missing_value, 4),

            (self._generate_percentage_approximation, 4),

            (self._generate_decimal, 3),

            (self._generate_fraction, 2),

            (self._generate_difference_square, 2),

            (self._generate_approximation, 1),

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


        return questions[
            :self.question_count
        ]



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

    def _generate_bodmas(self):

        a = random.randint(20, 100)
        b = random.randint(10, 50)
        c = random.randint(2, 20)
        d = random.randint(2, 15)


        patterns = [

            (
                f"{a} + {b} × {c} - {d}",
                a + b*c - d
            ),

            (
                f"({a}+{b}) × {c} - {d}",
                (a+b)*c-d
            ),

            (
                f"{a} × {b} ÷ {c} + {d}",
                (a*b)//c+d
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

    def _generate_missing_value(self):

        a = random.randint(20,80)
        b = random.randint(10,50)
        result = random.randint(100,500)


        answer = (
            a*b-result
        )


        return (

            f"({a} × {b}) - ? = {result}",

            str(answer),

            Difficulty.HARD,

        )



    # =========================================================
    # PERCENTAGE APPROXIMATION
    # =========================================================

    def _generate_percentage_approximation(self):

        patterns = [

            (
                "39.98% of 1002 × 50.02% of 498",
                100000
            ),

            (
                "49.98% of 998 + 25.02% of 402",
                600
            ),

            (
                "19.98% of 1001 × 25.01% of 400",
                20000
            ),

            (
                "9.99% of 1002 + 20.01% of 498",
                200
            ),

        ]


        expression, answer = random.choice(
            patterns
        )


        return (

            f"{expression} = ?",

            str(answer),

            Difficulty.HARD,

        )



    # =========================================================
    # DECIMAL
    # =========================================================

    def _generate_decimal(self):

        numbers = [

            round(
                random.uniform(10,90),
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
                map(str,numbers)
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

    def _generate_fraction(self):

        number = random.choice(
            [
                200,
                400,
                500,
                800,
            ]
        )


        fraction = random.choice(
            [
                "1/2",
                "3/5",
                "2/5",
                "3/4",
            ]
        )


        answer = (
            Fraction(fraction)
            *
            number
        )


        return (

            f"{fraction} of {number} = ?",

            str(int(answer)),

            Difficulty.MEDIUM,

        )



    # =========================================================
    # DIFFERENCE OF SQUARES
    # =========================================================

    def _generate_difference_square(self):

        a = random.choice(
            [
                10.01,
                12.01,
                15.01,
            ]
        )

        b = random.choice(
            [
                9.99,
                11.99,
                14.99,
            ]
        )


        answer = round(
            a*a-b*b,
            2
        )


        return (

            f"({a}² - {b}²) = ?",

            str(answer),

            Difficulty.HARD,

        )



    # =========================================================
    # APPROXIMATION
    # =========================================================

    def _generate_approximation(self):

        patterns = [

            (
                "12.2 + 12.6 + 12.8 + 12.3 + 12.1",
                62
            ),

            (
                "49.8 × 20",
                996
            ),

            (
                "99.5 × 10",
                995
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