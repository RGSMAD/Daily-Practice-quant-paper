"""
generator.py

Main orchestration service for the Daily Aptitude Generator.

Responsible for:
- Generating daily aptitude questions
- Managing history
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
    """Coordinates the complete daily generation workflow."""

    def __init__(self) -> None:
        """Initialize generator services."""

        self.question_bank = QuestionBank()

        self.history = HistoryManager()

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
        """Generate daily aptitude PDFs.

        Returns:
            Tuple[Path, Path]:
                Question PDF path and answer PDF path.
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


        question_pdf_path = (
            settings.paths.output_dir
            / settings.pdf.question_pdf_name
        )

        answer_pdf_path = (
            settings.paths.output_dir
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
        """Generate PDFs and send email."""

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
            "Daily aptitude email workflow completed."
        )



    def _generate_questions(
        self,
    ) -> List[Question]:
        """Generate unique questions.

        Returns:
            List[Question]:
                Generated aptitude questions.
        """

        questions = (
            self.question_bank.generate()
        )


        unique_questions = []


        for question in questions:

            if self.history.exists(
                question.question
            ):

                LOGGER.warning(
                    "Skipping duplicate question: %s",
                    question.question,
                )

                continue


            unique_questions.append(
                question
            )


        LOGGER.info(
            "Generated %s unique questions.",
            len(unique_questions),
        )


        return unique_questions



    @staticmethod
    def _create_answers(
        questions: List[Question],
    ) -> List[Answer]:
        """Create answer objects.

        Args:
            questions:
                Generated questions.

        Returns:
            List[Answer]:
                Answer objects.
        """

        return [
            Answer(
                question_id=question.id,
                answer=question.answer,
            )
            for question in questions
        ]