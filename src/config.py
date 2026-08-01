"""
config.py

Central configuration loader for the Daily Aptitude Generator.

Loads configuration from config.yaml and exposes a strongly typed
dataclass-based settings object.
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"


# ============================================================
# PATH CONFIGURATION
# ============================================================

@dataclass(slots=True, frozen=True)
class PathsConfig:

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
# OTHER CONFIGURATION
# ============================================================

@dataclass(slots=True, frozen=True)
class DifficultyConfig:

    easy_percentage: int
    medium_percentage: int
    hard_percentage: int


@dataclass(slots=True, frozen=True)
class EmailConfig:

    smtp_server: str
    smtp_port: int

    subject: str
    body: str

    sender_env: str
    password_env: str
    receiver_env: str

    use_tls: bool


@dataclass(slots=True, frozen=True)
class HistoryConfig:

    enabled: bool
    retain_days: int
    filename: str
    max_records: int


@dataclass(slots=True, frozen=True)
class LoggingConfig:

    level: str
    filename: str


@dataclass(slots=True, frozen=True)
class AppConfig:

    timezone: str
    app_name: str
    version: str


# ============================================================
# ROOT SETTINGS
# ============================================================

@dataclass(slots=True, frozen=True)
class Settings:

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
    Load YAML configuration.
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


def project_paths() -> PathsConfig:
    """
    Generate runtime paths.
    """

    return PathsConfig(
        project_root=PROJECT_ROOT,
        assets_dir=PROJECT_ROOT / "assets",
        output_dir=PROJECT_ROOT / "output",
        history_dir=PROJECT_ROOT / "history",
        logs_dir=PROJECT_ROOT / "logs",
    )


def history_file_path(
    paths: PathsConfig,
    history: HistoryConfig,
) -> Path:
    """
    Return complete history file location.
    """

    return paths.history_dir / history.filename


# ============================================================
# VALIDATION
# ============================================================

def validate_difficulty(
    difficulty: DifficultyConfig,
) -> None:

    total = (
        difficulty.easy_percentage
        + difficulty.medium_percentage
        + difficulty.hard_percentage
    )

    if total != 100:
        raise ValueError(
            "Difficulty percentages must total 100"
        )


# ============================================================
# SETTINGS LOADER
# ============================================================

def load_settings() -> Settings:

    config = load_yaml()

    paths = project_paths()

    pdf_data = config.get("pdf", {})
    question_data = config.get("questions", {})
    range_data = config.get("ranges", {})
    difficulty_data = config.get("difficulty", {})
    email_data = config.get("email", {})
    history_data = config.get("history", {})
    logging_data = config.get("logging", {})
    app_data = config.get("app", {})

    pdf = PDFConfig(
        title=pdf_data.get("title", ""),
        author=pdf_data.get("author", ""),
        subject=pdf_data.get("subject", ""),
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

    questions = QuestionConfig(
        **question_data
    )

    ranges = NumberRangeConfig(
        **range_data
    )

    difficulty = DifficultyConfig(
        **difficulty_data
    )

    validate_difficulty(difficulty)

    email = EmailConfig(
        **email_data
    )

    history = HistoryConfig(
        enabled=history_data.get(
            "enabled",
            True,
        ),
        retain_days=history_data.get(
            "retain_days",
            30,
        ),
        filename=history_data.get(
            "filename",
            "questions_history.json",
        ),
        max_records=history_data.get(
            "max_records",
            1000,
        ),
    )

    logging = LoggingConfig(
        **logging_data
    )

    app = AppConfig(
        **app_data
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
