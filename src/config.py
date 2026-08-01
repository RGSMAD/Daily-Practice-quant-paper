"""
config.py

Central configuration for the Daily Aptitude Generator.

This module contains all application-level configuration:
- Paths
- PDF settings
- Question generation settings
- Number ranges
- Email settings
- History settings
- Logging settings
- Application metadata
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from reportlab.lib.pagesizes import A4


# ============================================================
# PATH CONFIGURATION
# ============================================================


@dataclass(frozen=True)
class PathsConfig:
    """Project directory configuration."""

    project_root: Path = (
        Path(__file__).resolve().parent.parent
    )

    assets_dir: Path = field(init=False)

    output_dir: Path = field(init=False)

    history_dir: Path = field(init=False)

    logs_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        """Initialize project directories."""

        object.__setattr__(
            self,
            "assets_dir",
            self.project_root / "assets",
        )

        object.__setattr__(
            self,
            "output_dir",
            self.project_root / "output",
        )

        object.__setattr__(
            self,
            "history_dir",
            self.project_root / "history",
        )

        object.__setattr__(
            self,
            "logs_dir",
            self.project_root / "logs",
        )

        self.assets_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.history_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.logs_dir.mkdir(
            parents=True,
            exist_ok=True,
        )


# ============================================================
# PDF CONFIGURATION
# ============================================================


@dataclass(frozen=True)
class PDFConfig:
    """PDF generation configuration."""

    title: str = (
        "Daily Aptitude Practice"
    )

    author: str = (
        "Daily Aptitude Generator"
    )

    subject: str = (
        "Quantitative Aptitude"
    )

    page_size: tuple = A4

    font_name: str = "Helvetica"

    font_bold: str = (
        "Helvetica-Bold"
    )

    font_size: int = 11

    heading_size: int = 18

    line_spacing: int = 20

    margin: int = 40

    show_page_numbers: bool = True

    include_logo: bool = True

    logo_name: str = "logo.png"

    question_pdf_name: str = (
        "Daily_Practice.pdf"
    )

    answer_pdf_name: str = (
        "Daily_Practice_Answers.pdf"
    )


# ============================================================
# QUESTION CONFIGURATION
# ============================================================


@dataclass(frozen=True)
class QuestionConfig:
    """Question generation counts."""

    square_questions: int = 10

    cube_questions: int = 5

    square_root_questions: int = 10

    cube_root_questions: int = 10

    simplification_questions: int = 15

    series_questions: int = 15

    perfect_square_roots: int = 8

    non_perfect_square_roots: int = 2


# ============================================================
# NUMBER RANGE CONFIGURATION
# ============================================================


@dataclass(frozen=True)
class NumberRangeConfig:
    """Number ranges used for generation."""

    square_min: int = 10

    square_max: int = 999

    cube_min: int = 10

    cube_max: int = 999

    perfect_square_root_min: int = 10

    perfect_square_root_max: int = 50

    perfect_cube_root_min: int = 2

    perfect_cube_root_max: int = 20

    simplification_min_operand: int = 10

    simplification_max_operand: int = 500

    series_min_start: int = 1

    series_max_start: int = 100


# ============================================================
# DIFFICULTY CONFIGURATION
# ============================================================


@dataclass(frozen=True)
class DifficultyConfig:
    """Question difficulty distribution."""

    easy_percentage: int = 40

    medium_percentage: int = 40

    hard_percentage: int = 20


# ============================================================
# EMAIL CONFIGURATION
# ============================================================


@dataclass(frozen=True)
class EmailConfig:
    """Email delivery configuration."""

    smtp_server: str = (
        "smtp.gmail.com"
    )

    smtp_port: int = 587

    subject: str = (
        "Daily Aptitude Practice"
    )

    body: str = (
        "Hello,\n\n"
        "Please find today's aptitude "
        "practice sheet attached.\n\n"
        "Happy Learning!"
    )

    sender_env: str = (
        "EMAIL_USER"
    )

    password_env: str = (
        "EMAIL_PASSWORD"
    )

    receiver_env: str = (
        "RECEIVER_EMAIL"
    )

    use_tls: bool = True


# ============================================================
# HISTORY CONFIGURATION
# ============================================================


@dataclass(frozen=True)
class HistoryConfig:
    """Question history configuration."""

    enabled: bool = True

    retain_days: int = 30

    filename: str = (
        "history.json"
    )


# ============================================================
# LOGGING CONFIGURATION
# ============================================================


@dataclass(frozen=True)
class LoggingConfig:
    """Application logging configuration."""

    level: str = "INFO"

    filename: str = (
        "generator.log"
    )


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================


@dataclass(frozen=True)
class AppConfig:
    """Application metadata."""

    timezone: str = (
        "Asia/Kolkata"
    )

    app_name: str = (
        "Daily Aptitude Generator"
    )

    version: str = (
        "1.0.0"
    )


# ============================================================
# ROOT SETTINGS
# ============================================================


@dataclass(frozen=True)
class Settings:
    """Complete application settings."""

    paths: PathsConfig = field(
        default_factory=PathsConfig
    )

    pdf: PDFConfig = field(
        default_factory=PDFConfig
    )

    questions: QuestionConfig = field(
        default_factory=QuestionConfig
    )

    ranges: NumberRangeConfig = field(
        default_factory=NumberRangeConfig
    )

    difficulty: DifficultyConfig = field(
        default_factory=DifficultyConfig
    )

    email: EmailConfig = field(
        default_factory=EmailConfig
    )

    history: HistoryConfig = field(
        default_factory=HistoryConfig
    )

    logging: LoggingConfig = field(
        default_factory=LoggingConfig
    )

    app: AppConfig = field(
        default_factory=AppConfig
    )


settings = Settings()