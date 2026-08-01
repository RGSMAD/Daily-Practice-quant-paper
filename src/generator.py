"""
generator.py

Main orchestration service for the
Daily Aptitude Generator.

Responsible for:
- Generating unique aptitude questions
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
from src.models.answer import Answer
from src.models.question import Question
from src.pdf.answer_pdf import AnswerPDFGenerator
from src.pdf.question_pdf import QuestionPDFGenerator
from src.utils.history import HistoryManager
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class AptitudeGenerator:
    """
    Coordinates the complete daily
    aptitude generation workflow.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize application services.
        """

        self.history = (
            HistoryManager()
        )

        self.question_bank = (
            QuestionBank()
        )

        self.question_pdf = (
            QuestionPDFGenerator()
        )

        self.answer_pdf = (
            AnswerPDFGenerator()
        )

        self.email_sender = (
            EmailSender()
        )


    def generate(
        self,
    ) -> Tuple[
        Path,
        Path,
    ]:
        """
        Generate daily aptitude PDFs.
        """

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


    def generate_and_send(
        self,
    ) -> None:
        """
        Generate PDFs and email them.
        """

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


    def _generate_questions(
        self,
    ) -> List[Question]:
        """
        Generate the exact configured number
        of unique questions.

        Question order is preserved so that
        questions remain grouped by generator
        type in the PDF.

        Duplicate questions found in history
        or the current batch are rejected and
        replaced by newly generated questions.
        """

        required_count = (
            self._get_required_question_count()
        )

        selected_questions: List[
            Question
        ] = []


        while len(selected_questions) < required_count:

            question_pool = (
                self.question_bank.generate()
            )


            for question in question_pool:

                if len(selected_questions) >= required_count:
                    break


                if self._is_duplicate(
                    question,
                    selected_questions,
                ):

                    LOGGER.info(
                        "Duplicate question rejected."
                    )

                    continue


                selected_questions.append(
                    question
                )


        self._reassign_ids(
            selected_questions
        )


        LOGGER.info(
            "Generated %s unique questions.",
            len(selected_questions),
        )


        return selected_questions


    def _is_duplicate(
        self,
        question: Question,
        current_questions: List[Question],
    ) -> bool:
        """
        Check duplicate against history
        and current generation batch.
        """

        if self.history.is_duplicate(
            question
        ):
            return True


        return any(
            existing.fingerprint
            == question.fingerprint
            for existing
            in current_questions
        )


    @staticmethod
    def _get_required_question_count() -> int:
        """
        Calculate total configured
        daily question count.
        """

        return (
            settings.questions.square_questions
            + settings.questions.cube_questions
            + settings.questions.square_root_questions
            + settings.questions.cube_root_questions
            + settings.questions.simplification_questions
            + settings.questions.series_questions
        )


    @staticmethod
    def _reassign_ids(
        questions: List[Question],
    ) -> None:
        """
        Assign sequential IDs after
        duplicate filtering.
        """

        for index, question in enumerate(
            questions,
            start=1,
        ):

            question.id = index


    @staticmethod
    def _create_answers(
        questions: List[Question],
    ) -> List[Answer]:
        """
        Create answer objects from
        generated questions.
        """

        answers: List[
            Answer
        ] = []


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
