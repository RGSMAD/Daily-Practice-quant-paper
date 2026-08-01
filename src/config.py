"""
config.py

Central configuration loader for the Daily Aptitude Generator.

Configuration values are loaded from config.yaml while preserving a
strongly-typed dataclass interface throughout the application.

Example:
    from src.config import settings

    print(settings.pdf.title)
    print(settings.questions.square_questions)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from reportlab.lib.pagesizes import A4


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILE = PROJECT_ROOT / "config.yaml"


# ============================================================
# PATH CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class PathsConfig:
    """
    Runtime project paths.

    These values are derived automatically from the project root
    and therefore are not stored inside config.yaml.
    """

    project_root: Path

    assets_dir: Path

    output_dir: Path

    history_dir: Path

    logs_dir: Path


# ============================================================
# PDF CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class PDFConfig:
    """
    PDF generation configuration.
    """

    title: str

    author: str

    subject: str

    page_size: tuple = A4

    font_name: str = "Helvetica"

    font_bold: str = "Helvetica-Bold"

    font_size: int = 11

    heading_size: int = 18

    line_spacing: int = 20

    margin: int = 40

    show_page_numbers: bool = True

    include_logo: bool = True

    logo_name: str = "logo.png"

    question_pdf_name: str = "Daily_Practice.pdf"

    answer_pdf_name: str = (
        "Daily_Practice_Answers.pdf"
    )


# ============================================================
# QUESTION CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class QuestionConfig:
    """
    Question generation configuration.
    """

    square_questions: int

    cube_questions: int

    square_root_questions: int

    cube_root_questions: int

    simplification_questions: int

    series_questions: int

    perfect_square_roots: int

    non_perfect_square_roots: int


# ============================================================
# NUMBER RANGE CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class NumberRangeConfig:
    """
    Number ranges used by generators.
    """

    square_min: int

    square_max: int

    cube_min: int

    cube_max: int

    perfect_square_root_min: int

    perfect_square_root_max: int

    perfect_cube_root_min: int

    perfect_cube_root_max: int

    simplification_min_operand: int

    simplification_max_operand: int

    series_min_start: int

    series_max_start: int


# ============================================================
# DIFFICULTY CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class DifficultyConfig:
    """
    Difficulty distribution.
    """

    easy_percentage: int

    medium_percentage: int

    hard_percentage: int


# ============================================================
# EMAIL CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class EmailConfig:
    """
    Email configuration.
    """

    smtp_server: str

    smtp_port: int

    subject: str

    body: str

    sender_env: str

    password_env: str

    receiver_env: str

    use_tls: bool


# ============================================================
# HISTORY CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class HistoryConfig:
    """
    Question history configuration.
    """

    enabled: bool

    retain_days: int

    filename: str


# ============================================================
# LOGGING CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class LoggingConfig:
    """
    Logging configuration.
    """

    level: str

    filename: str


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class AppConfig:
    """
    Application metadata.
    """

    timezone: str

    app_name: str

    version: str


# ============================================================
# ROOT SETTINGS
# ============================================================


@dataclass(slots=True, frozen=True)
class Settings:
    """
    Complete application configuration.
    """

    paths: PathsConfig

    pdf: PDFConfig

    questions: QuestionConfig

    ranges: NumberRangeConfig

    difficulty: DifficultyConfig

    email: EmailConfig

    history: HistoryConfig

    logging: LoggingConfig

    app: AppConfig


# ============================================================
# YAML HELPERS
# ============================================================


def load_yaml() -> dict[str, Any]:
    """
    Load configuration from config.yaml.

    Returns:
        Parsed YAML configuration.

    Raises:
        FileNotFoundError:
            If config.yaml does not exist.
    """

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: "
            f"{CONFIG_FILE}"
        )

    with CONFIG_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        return yaml.safe_load(file)


def project_paths() -> PathsConfig:
    """
    Build runtime project paths.

    Returns:
        PathsConfig instance.
    """

    return PathsConfig(
        project_root=PROJECT_ROOT,
        assets_dir=PROJECT_ROOT / "assets",
        output_dir=PROJECT_ROOT / "output",
        history_dir=PROJECT_ROOT / "history",
        logs_dir=PROJECT_ROOT / "logs",
    )

# ============================================================
# SETTINGS LOADER
# ============================================================


def load_settings() -> Settings:
    """
    Load application settings from config.yaml.

    Returns:
        Fully initialized Settings object.
    """

    config = load_yaml()

    paths = project_paths()

    pdf = PDFConfig(
        title=config["pdf"]["title"],
        author=config["pdf"]["author"],
        subject=config["pdf"]["subject"],
        font_name=config["pdf"]["font_name"],
        font_bold=config["pdf"]["font_bold"],
        font_size=config["pdf"]["font_size"],
        heading_size=config["pdf"]["heading_size"],
        line_spacing=config["pdf"]["line_spacing"],
        margin=config["pdf"]["margin"],
        show_page_numbers=config["pdf"]["show_page_numbers"],
        include_logo=config["pdf"]["include_logo"],
        logo_name=config["pdf"]["logo_name"],
        question_pdf_name=config["pdf"]["question_pdf_name"],
        answer_pdf_name=config["pdf"]["answer_pdf_name"],
    )

    questions = QuestionConfig(
        square_questions=config["questions"]["square_questions"],
        cube_questions=config["questions"]["cube_questions"],
        square_root_questions=config["questions"]["square_root_questions"],
        cube_root_questions=config["questions"]["cube_root_questions"],
        simplification_questions=config["questions"]["simplification_questions"],
        series_questions=config["questions"]["series_questions"],
        perfect_square_roots=config["questions"]["perfect_square_roots"],
        non_perfect_square_roots=config["questions"]["non_perfect_square_roots"],
    )

    ranges = NumberRangeConfig(
        square_min=config["ranges"]["square_min"],
        square_max=config["ranges"]["square_max"],
        cube_min=config["ranges"]["cube_min"],
        cube_max=config["ranges"]["cube_max"],
        perfect_square_root_min=config["ranges"]["perfect_square_root_min"],
        perfect_square_root_max=config["ranges"]["perfect_square_root_max"],
        perfect_cube_root_min=config["ranges"]["perfect_cube_root_min"],
        perfect_cube_root_max=config["ranges"]["perfect_cube_root_max"],
        simplification_min_operand=config["ranges"]["simplification_min_operand"],
        simplification_max_operand=config["ranges"]["simplification_max_operand"],
        series_min_start=config["ranges"]["series_min_start"],
        series_max_start=config["ranges"]["series_max_start"],
    )

    difficulty = DifficultyConfig(
        easy_percentage=config["difficulty"]["easy_percentage"],
        medium_percentage=config["difficulty"]["medium_percentage"],
        hard_percentage=config["difficulty"]["hard_percentage"],
    )

    email = EmailConfig(
        smtp_server=config["email"]["smtp_server"],
        smtp_port=config["email"]["smtp_port"],
        subject=config["email"]["subject"],
        body=config["email"]["body"],
        sender_env=config["email"]["sender_env"],
        password_env=config["email"]["password_env"],
        receiver_env=config["email"]["receiver_env"],
        use_tls=config["email"]["use_tls"],
    )

    history = HistoryConfig(
        enabled=config["history"]["enabled"],
        retain_days=config["history"]["retain_days"],
        filename=config["history"]["filename"],
    )

    logging = LoggingConfig(
        level=config["logging"]["level"],
        filename=config["logging"]["filename"],
    )

    app = AppConfig(
        timezone=config["app"]["timezone"],
        app_name=config["app"]["app_name"],
        version=config["app"]["version"],
    )

    return Settings(
        paths=paths,
        pdf=pdf,
        questions=questions,
        ranges=ranges,
        difficulty=difficulty,
        email=email,
        history=history,
        logging=logging,
        app=app,
    )


# ============================================================
# GLOBAL SETTINGS
# ============================================================

settings = load_settings()