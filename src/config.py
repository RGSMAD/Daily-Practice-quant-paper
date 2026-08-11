"""
config.py

Central configuration loader for the
Daily Aptitude Generator.

Loads configuration from config.yaml and exposes
a strongly typed dataclass-based settings object.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from reportlab.lib.pagesizes import A4


# ============================================================
# PROJECT ROOT
# ============================================================


def find_project_root() -> Path:
    """
    Locate the project root by searching for config.yaml.
    """

    current = Path(__file__).resolve()

    for parent in current.parents:
        if (parent / "config.yaml").exists():
            return parent

    raise FileNotFoundError(
        "Could not locate project root containing config.yaml"
    )


PROJECT_ROOT = find_project_root()
CONFIG_FILE = PROJECT_ROOT / "config.yaml"


# ============================================================
# PATH CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class PathsConfig:
    """
    Runtime project paths.
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

    page_size: tuple[Any, Any] = A4

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
    answer_pdf_name: str = "Daily_Practice_Answers.pdf"


# ============================================================
# QUESTION CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class QuestionConfig:
    """
    Daily question counts and distributions.
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
# RANGE CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class NumberRangeConfig:
    """
    Number ranges used by question generators.
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
    Weekly active-history configuration.

    active_file:
        File containing the current week's questions.

    archive_directory:
        Directory where completed weekly history
        is archived after Sunday revision.

    archive_monthly:
        If enabled, archives are placed inside
        YYYY-MM monthly directories.
    """

    enabled: bool
    active_file: str
    archive_directory: str
    archive_monthly: bool


# ============================================================
# WEEKLY REVISION CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class RevisionConfig:
    """
    Weekly revision configuration.
    """

    enabled: bool
    revision_day: str
    questions_per_topic: int


# ============================================================
# LOGGING CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class LoggingConfig:
    """
    Application logging configuration.
    """

    level: str
    filename: str


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================


@dataclass(slots=True, frozen=True)
class AppConfig:
    """
    Application-level configuration.
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
    revision: RevisionConfig
    logging: LoggingConfig
    app: AppConfig


# ============================================================
# YAML LOADER
# ============================================================


def load_yaml() -> dict[str, Any]:
    """
    Load YAML configuration from config.yaml.
    """

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file) or {}


# ============================================================
# PROJECT PATHS
# ============================================================


def project_paths() -> PathsConfig:
    """
    Generate runtime project paths.
    """

    return PathsConfig(
        project_root=PROJECT_ROOT,
        assets_dir=PROJECT_ROOT / "assets",
        output_dir=PROJECT_ROOT / "output",
        history_dir=PROJECT_ROOT / "history",
        logs_dir=PROJECT_ROOT / "logs",
    )


# ============================================================
# VALIDATION
# ============================================================


def validate_difficulty(
    difficulty: DifficultyConfig,
) -> None:
    """
    Ensure difficulty percentages total 100%.
    """

    total = (
        difficulty.easy_percentage
        + difficulty.medium_percentage
        + difficulty.hard_percentage
    )

    if total != 100:
        raise ValueError(
            "Difficulty percentages must total 100"
        )


def validate_history(
    history: HistoryConfig,
) -> None:
    """
    Validate history configuration.
    """

    if not history.active_file.strip():
        raise ValueError(
            "History active_file cannot be empty."
        )

    if not history.archive_directory.strip():
        raise ValueError(
            "History archive_directory cannot be empty."
        )


def validate_revision(
    revision: RevisionConfig,
) -> None:
    """
    Validate weekly revision configuration.
    """

    if revision.questions_per_topic < 1:
        raise ValueError(
            "revision.questions_per_topic must be at least 1."
        )

    if not revision.revision_day.strip():
        raise ValueError(
            "revision.revision_day cannot be empty."
        )


# ============================================================
# SETTINGS LOADER
# ============================================================


def load_settings() -> Settings:
    """
    Load and validate complete application configuration.
    """

    config = load_yaml()

    paths = project_paths()

    pdf_data = config.get("pdf", {})
    question_data = config.get("questions", {})
    range_data = config.get("ranges", {})
    difficulty_data = config.get("difficulty", {})
    email_data = config.get("email", {})
    history_data = config.get("history", {})
    revision_data = config.get("revision", {})
    logging_data = config.get("logging", {})
    app_data = config.get("app", {})

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    pdf = PDFConfig(
        title=pdf_data.get(
            "title",
            "Daily Aptitude Practice",
        ),
        author=pdf_data.get(
            "author",
            "Daily Aptitude Generator",
        ),
        subject=pdf_data.get(
            "subject",
            "Quantitative Aptitude",
        ),
        font_name=pdf_data.get(
            "font_name",
            "Helvetica",
        ),
        font_bold=pdf_data.get(
            "font_bold",
            "Helvetica-Bold",
        ),
        font_size=pdf_data.get(
            "font_size",
            11,
        ),
        heading_size=pdf_data.get(
            "heading_size",
            18,
        ),
        line_spacing=pdf_data.get(
            "line_spacing",
            20,
        ),
        margin=pdf_data.get(
            "margin",
            40,
        ),
        show_page_numbers=pdf_data.get(
            "show_page_numbers",
            True,
        ),
        include_logo=pdf_data.get(
            "include_logo",
            True,
        ),
        logo_name=pdf_data.get(
            "logo_name",
            "logo.png",
        ),
        question_pdf_name=pdf_data.get(
            "question_pdf_name",
            "Daily_Practice.pdf",
        ),
        answer_pdf_name=pdf_data.get(
            "answer_pdf_name",
            "Daily_Practice_Answers.pdf",
        ),
    )

    # --------------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------------

    questions = QuestionConfig(
        square_questions=question_data.get(
            "square_questions",
            10,
        ),
        cube_questions=question_data.get(
            "cube_questions",
            10,
        ),
        square_root_questions=question_data.get(
            "square_root_questions",
            10,
        ),
        cube_root_questions=question_data.get(
            "cube_root_questions",
            10,
        ),
        simplification_questions=question_data.get(
            "simplification_questions",
            20,
        ),
        series_questions=question_data.get(
            "series_questions",
            15,
        ),
        perfect_square_roots=question_data.get(
            "perfect_square_roots",
            8,
        ),
        non_perfect_square_roots=question_data.get(
            "non_perfect_square_roots",
            2,
        ),
    )

    # --------------------------------------------------------
    # RANGES
    # --------------------------------------------------------

    ranges = NumberRangeConfig(
        square_min=range_data.get(
            "square_min",
            10,
        ),
        square_max=range_data.get(
            "square_max",
            500,
        ),
        cube_min=range_data.get(
            "cube_min",
            10,
        ),
        cube_max=range_data.get(
            "cube_max",
            250,
        ),
        perfect_square_root_min=range_data.get(
            "perfect_square_root_min",
            10,
        ),
        perfect_square_root_max=range_data.get(
            "perfect_square_root_max",
            300,
        ),
        perfect_cube_root_min=range_data.get(
            "perfect_cube_root_min",
            2,
        ),
        perfect_cube_root_max=range_data.get(
            "perfect_cube_root_max",
            100,
        ),
        simplification_min_operand=range_data.get(
            "simplification_min_operand",
            10,
        ),
        simplification_max_operand=range_data.get(
            "simplification_max_operand",
            500,
        ),
        series_min_start=range_data.get(
            "series_min_start",
            1,
        ),
        series_max_start=range_data.get(
            "series_max_start",
            100,
        ),
    )

    # --------------------------------------------------------
    # DIFFICULTY
    # --------------------------------------------------------

    difficulty = DifficultyConfig(
        easy_percentage=difficulty_data.get(
            "easy_percentage",
            40,
        ),
        medium_percentage=difficulty_data.get(
            "medium_percentage",
            40,
        ),
        hard_percentage=difficulty_data.get(
            "hard_percentage",
            20,
        ),
    )

    validate_difficulty(difficulty)

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    email = EmailConfig(
        smtp_server=email_data.get(
            "smtp_server",
            "smtp.gmail.com",
        ),
        smtp_port=email_data.get(
            "smtp_port",
            587,
        ),
        subject=email_data.get(
            "subject",
            "Daily Aptitude Practice",
        ),
        body=email_data.get(
            "body",
            "Please find today's aptitude practice sheet attached.",
        ),
        sender_env=email_data.get(
            "sender_env",
            "EMAIL_USER",
        ),
        password_env=email_data.get(
            "password_env",
            "EMAIL_PASSWORD",
        ),
        receiver_env=email_data.get(
            "receiver_env",
            "RECEIVER_EMAIL",
        ),
        use_tls=email_data.get(
            "use_tls",
            True,
        ),
    )

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    history = HistoryConfig(
        enabled=history_data.get(
            "enabled",
            True,
        ),
        active_file=history_data.get(
            "active_file",
            "active.json",
        ),
        archive_directory=history_data.get(
            "archive_directory",
            "archive",
        ),
        archive_monthly=history_data.get(
            "archive_monthly",
            True,
        ),
    )

    validate_history(history)

    # --------------------------------------------------------
    # WEEKLY REVISION
    # --------------------------------------------------------

    revision = RevisionConfig(
        enabled=revision_data.get(
            "enabled",
            True,
        ),
        revision_day=revision_data.get(
            "revision_day",
            "Sunday",
        ),
        questions_per_topic=revision_data.get(
            "questions_per_topic",
            5,
        ),
    )

    validate_revision(revision)

    # --------------------------------------------------------
    # LOGGING
    # --------------------------------------------------------

    logging_config = LoggingConfig(
        level=logging_data.get(
            "level",
            "INFO",
        ),
        filename=logging_data.get(
            "filename",
            "generator.log",
        ),
    )

    # --------------------------------------------------------
    # APPLICATION
    # --------------------------------------------------------

    app = AppConfig(
        timezone=app_data.get(
            "timezone",
            "Asia/Kolkata",
        ),
        app_name=app_data.get(
            "app_name",
            "Daily Aptitude Generator",
        ),
        version=app_data.get(
            "version",
            "1.0.0",
        ),
    )

    # --------------------------------------------------------
    # FINAL SETTINGS
    # --------------------------------------------------------

    return Settings(
        paths=paths,
        pdf=pdf,
        questions=questions,
        ranges=ranges,
        difficulty=difficulty,
        email=email,
        history=history,
        revision=revision,
        logging=logging_config,
        app=app,
    )


# ============================================================
# GLOBAL SETTINGS
# ============================================================

settings = load_settings()
