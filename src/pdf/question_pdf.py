
"""
question_pdf.py

Generates aptitude practice question PDFs.

The same generator is used for:
- Daily aptitude practice
- Weekly revision practice
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

        self._register_fonts()

        self.page_width, self.page_height = A4

        self.margin = settings.pdf.margin

    # =========================================================
    # FONT REGISTRATION
    # =========================================================

    def _register_fonts(self) -> None:
        """
        Register Unicode fonts for mathematical symbols.
        """

        regular_font = (
            settings.paths.assets_dir
            / "fonts"
            / "DejaVuSans.ttf"
        )

        bold_font = (
            settings.paths.assets_dir
            / "fonts"
            / "DejaVuSans-Bold.ttf"
        )

        if not regular_font.exists():
            raise FileNotFoundError(
                f"Regular font not found: {regular_font}"
            )

        if not bold_font.exists():
            raise FileNotFoundError(
                f"Bold font not found: {bold_font}"
            )

        if "DejaVuSans" not in pdfmetrics.getRegisteredFontNames():

            pdfmetrics.registerFont(
                TTFont(
                    "DejaVuSans",
                    str(regular_font),
                )
            )

        if (
            "DejaVuSans-Bold"
            not in pdfmetrics.getRegisteredFontNames()
        ):

            pdfmetrics.registerFont(
                TTFont(
                    "DejaVuSans-Bold",
                    str(bold_font),
                )
            )

    # =========================================================
    # MAIN PDF GENERATOR
    # =========================================================

    def generate(
        self,
        questions: List[Question],
        output_path: Path,
        title: str | None = None,
    ) -> Path:
        """
        Generate question PDF.

        Args:
            questions:
                Questions to include in the PDF.

            output_path:
                Destination PDF path.

            title:
                Optional PDF/header title.

                If omitted, the configured daily
                aptitude title is used.

        Returns:
            Path:
                Generated PDF path.
        """

        LOGGER.info(
            "Generating question PDF: %s",
            output_path,
        )

        pdf = canvas.Canvas(
            str(output_path),
            pagesize=A4,
        )

        pdf.setTitle(
            title
            if title is not None
            else settings.pdf.title
        )

        pdf.setAuthor(
            settings.pdf.author
        )

        pdf.setSubject(
            settings.pdf.subject
        )

        document_title = (
            title
            if title is not None
            else settings.pdf.title
        )

        self._draw_header(
            pdf,
            document_title,
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
                    pdf,
                    document_title,
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
    # MATH FORMATTER
    # =========================================================

    def _format_math_symbols(
        self,
        text: str,
    ) -> str:
        """
        Convert LaTeX-style notation
        into PDF-friendly symbols.
        """

        # -----------------------------------------------------
        # Cube root
        #
        # \sqrt[3]{4096}
        #
        # becomes:
        # ³√4096
        # -----------------------------------------------------

        text = re.sub(
            r"\\sqrt\[3\]\{(\d+)\}",
            r"³√\1",
            text,
        )

        # -----------------------------------------------------
        # Square root
        #
        # \sqrt{625}
        #
        # becomes:
        # √625
        # -----------------------------------------------------

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
        title: str,
    ) -> None:
        """
        Draw PDF header.

        Args:
            pdf:
                ReportLab canvas object.

            title:
                Header title.
        """

        pdf.setFont(
            settings.pdf.font_bold,
            settings.pdf.heading_size,
        )

        pdf.drawString(
            self.margin,
            self.page_height - self.margin,
            title,
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
