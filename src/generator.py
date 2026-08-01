"""
generator.py

Main orchestration service for the
Daily Aptitude Generator.

Responsible for:
- Generating aptitude questions
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

        self.question_bank = (
            QuestionBank()
        )

        self.history = (
            HistoryManager()
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

        Returns:
            Tuple containing
            question PDF path and
            answer PDF path.
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
        Generate PDFs and
        email them.
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
        Generate unique aptitude questions.

        Returns:
            List of unique questions.
        """

        generated_questions = (
            self.question_bank.generate()
        )

        unique_questions: List[
            Question
        ] = []

        for question in generated_questions:

            if self.history.is_duplicate(
                question
            ):

                LOGGER.warning(
                    "Duplicate question skipped: %s",
                    question.question,
                )

                continue

            unique_questions.append(
                question
            )

        LOGGER.info(
            "Generated %s unique questions.",
            len(
                unique_questions
            ),
        )

        return unique_questions


    @staticmethod
    def _create_answers(
        questions: List[
            Question
        ],
    ) -> List[
        Answer
    ]:
        """
        Create answer objects from
        generated questions.

        Args:
            questions:
                Generated questions.

        Returns:
            List of Answer objects.
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