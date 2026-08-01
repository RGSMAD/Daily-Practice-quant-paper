"""
question_pdf.py

Generates the daily aptitude practice question PDF.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from src.config import settings
from src.models.question import Question
from src.utils.logger import get_logger


LOGGER = get_logger(__name__)


class QuestionPDFGenerator:
    """
    Generates PDF containing aptitude questions.
    """

    def __init__(self) -> None:
        """
        Initialize PDF configuration.
        """

        self.page_width, self.page_height = A4

        self.margin = (
            settings.pdf.margin
        )


    # =========================================================
    # MAIN PDF GENERATOR
    # =========================================================

    def generate(
        self,
        questions: List[Question],
        output_path: Path,
    ) -> Path:
        """
        Generate question PDF.
        """

        LOGGER.info(
            "Generating question PDF."
        )


        pdf = canvas.Canvas(
            str(output_path),
            pagesize=A4,
        )


        pdf.setTitle(
            settings.pdf.title
        )

        pdf.setAuthor(
            settings.pdf.author
        )

        pdf.setSubject(
            settings.pdf.subject
        )


        self._draw_header(
            pdf
        )


        y_position = (
            self.page_height
            - self.margin * 2
        )


        for index, question in enumerate(
            questions,
            start=1,
        ):


            if y_position < 80:

                self._add_page_number(
                    pdf
                )

                pdf.showPage()

                self._draw_header(
                    pdf
                )

                y_position = (
                    self.page_height
                    - self.margin * 2
                )


            formatted_question = (
                self._format_math_symbols(
                    question.question
                )
            )


            text = (
                f"{index}. "
                f"{formatted_question}"
            )


            pdf.setFont(
                settings.pdf.font_name,
                settings.pdf.font_size,
            )


            pdf.drawString(
                self.margin,
                y_position,
                text,
            )


            y_position -= (
                settings.pdf.line_spacing
            )


        self._add_page_number(
            pdf
        )


        pdf.save()


        LOGGER.info(
            "Question PDF created: %s",
            output_path,
        )


        return output_path



    # =========================================================
    # MATH SYMBOL FORMATTER
    # =========================================================

    def _format_math_symbols(
        self,
        text: str,
    ) -> str:
        """
        Convert LaTeX-like math notation
        into PDF-friendly symbols.
        """

        # Cube root
        text = re.sub(
            r"\\sqrt\[3\]\{(\d+)\}",
            r"∛\1",
            text,
        )


        # Square root
        text = re.sub(
            r"\\sqrt\{(\d+)\}",
            r"√\1",
            text,
        )


        return text



    # =========================================================
    # HEADER
    # =========================================================

    def _draw_header(
        self,
        pdf: canvas.Canvas,
    ) -> None:
        """
        Draw PDF header.
        """

        pdf.setFont(
            settings.pdf.font_bold,
            settings.pdf.heading_size,
        )


        pdf.drawString(
            self.margin,
            self.page_height - self.margin,
            settings.pdf.title,
        )



    # =========================================================
    # PAGE NUMBER
    # =========================================================

    def _add_page_number(
        self,
        pdf: canvas.Canvas,
    ) -> None:
        """
        Add page number.
        """

        if not settings.pdf.show_page_numbers:

            return


        page_number = (
            pdf.getPageNumber()
        )


        pdf.setFont(
            settings.pdf.font_name,
            9,
        )


        pdf.drawRightString(
            self.page_width - self.margin,
            25,
            f"Page {page_number}",
        )