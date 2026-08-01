"""
generator.py

Main orchestration service for the
Daily Aptitude Generator.

Responsible for:
- Generating daily aptitude questions
- Managing question history
- Creating PDFs
- Sending email notifications
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from src.config import settings
from src.email.mailer import EmailSender

from src.generators.question_bank import QuestionBank

from src.generators.square_generator import SquareGenerator
from src.generators.cube_generator import CubeGenerator
from src.generators.square_root_generator import SquareRootGenerator
from src.generators.cube_root_generator import CubeRootGenerator
from src.generators.simplification_generator import SimplificationGenerator
from src.generators.series_generator import SeriesGenerator

from src.models.answer import Answer
from src.models.question import Question

from src.pdf.answer_pdf import AnswerPDFGenerator
from src.pdf.question_pdf import QuestionPDFGenerator

from src.utils.history import HistoryManager
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class AptitudeGenerator:
    """
    Coordinates complete aptitude generation workflow.
    """


    def __init__(self) -> None:

        self.history = HistoryManager()

        self.question_bank = QuestionBank()

        self.question_pdf = QuestionPDFGenerator()

        self.answer_pdf = AnswerPDFGenerator()

        self.email_sender = EmailSender()



    # =========================================================
    # MAIN GENERATION FLOW
    # =========================================================

    def generate(
        self,
    ) -> Tuple[Path, Path]:


        LOGGER.info(
            "Starting daily aptitude generation."
        )


        questions = (
            self._generate_questions()
        )


        self.history.add_questions(
            questions
        )

        self.history.save()


        answers = (
            self._create_answers(
                questions
            )
        )


        output_dir = (
            settings.paths.output_dir
        )


        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )


        question_pdf_path = (
            output_dir
            / settings.pdf.question_pdf_name
        )


        answer_pdf_path = (
            output_dir
            / settings.pdf.answer_pdf_name
        )


        self.question_pdf.generate(
            questions,
            question_pdf_path,
        )


        self.answer_pdf.generate(
            answers,
            answer_pdf_path,
        )


        LOGGER.info(
            "PDF generation completed."
        )


        return (
            question_pdf_path,
            answer_pdf_path,
        )



    # =========================================================
    # EMAIL
    # =========================================================

    def generate_and_send(
        self,
    ) -> None:


        question_pdf, answer_pdf = (
            self.generate()
        )


        self.email_sender.send(
            [
                question_pdf,
                answer_pdf,
            ]
        )


        LOGGER.info(
            "Daily aptitude email completed."
        )



    # =========================================================
    # QUESTION GENERATION
    # =========================================================

    def _generate_questions(
        self,
    ) -> List[Question]:

        """
        Generate questions category-wise.

        Duplicate questions are replaced
        from the same category.
        """


        generator_config = [

            (
                SquareGenerator(),
                settings.questions.square_questions,
            ),

            (
                CubeGenerator(),
                settings.questions.cube_questions,
            ),

            (
                SquareRootGenerator(),
                settings.questions.square_root_questions,
            ),

            (
                CubeRootGenerator(),
                settings.questions.cube_root_questions,
            ),

            (
                SimplificationGenerator(),
                settings.questions.simplification_questions,
            ),

            (
                SeriesGenerator(),
                settings.questions.series_questions,
            ),
        ]


        selected_questions: List[Question] = []


        for generator, required_count in generator_config:


            category_questions: List[
                Question
            ] = []


            attempts = 0


            while len(category_questions) < required_count:


                attempts += 1


                if attempts > 100:

                    raise RuntimeError(
                        f"Unable to generate enough "
                        f"unique questions for "
                        f"{generator.__class__.__name__}"
                    )


                generated = (
                    generator.generate()
                )


                for question in generated:


                    if len(category_questions) >= required_count:
                        break


                    if self._is_duplicate(
                        question,
                        selected_questions
                        +
                        category_questions,
                    ):

                        LOGGER.info(
                            "Duplicate rejected: %s",
                            question.question,
                        )

                        continue


                    category_questions.append(
                        question
                    )


            LOGGER.info(
                "%s finalized %s questions",
                generator.__class__.__name__,
                len(category_questions),
            )


            selected_questions.extend(
                category_questions
            )



        self._reassign_ids(
            selected_questions
        )


        LOGGER.info(
            "Generated %s unique questions.",
            len(selected_questions),
        )


        return selected_questions



    # =========================================================
    # DUPLICATE CHECK
    # =========================================================

    def _is_duplicate(
        self,
        question: Question,
        current_questions: List[Question],
    ) -> bool:


        if self.history.is_duplicate(
            question
        ):

            return True


        return any(
            existing.fingerprint
            ==
            question.fingerprint

            for existing in current_questions
        )



    # =========================================================
    # IDS
    # =========================================================

    @staticmethod
    def _reassign_ids(
        questions: List[Question],
    ) -> None:


        for index, question in enumerate(
            questions,
            start=1,
        ):

            question.id = index



    # =========================================================
    # ANSWERS
    # =========================================================

    @staticmethod
    def _create_answers(
        questions: List[Question],
    ) -> List[Answer]:


        answers: List[Answer] = []


        for question in questions:

            answers.append(
                Answer(
                    question_id=question.id,

                    question_type=(
                        question.question_type
                    ),

                    question=(
                        question.question
                    ),

                    answer=(
                        question.answer
                    ),
                )
            )


        return answers