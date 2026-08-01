"""
enums.py

Centralized enumerations used throughout the
Daily Aptitude Generator.
"""

from enum import Enum


# ============================================================
# Difficulty
# ============================================================

class Difficulty(str, Enum):

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ============================================================
# Question Sections
# ============================================================

class QuestionType(str, Enum):

    SQUARE = "square"

    CUBE = "cube"

    SQUARE_ROOT = "square_root"

    CUBE_ROOT = "cube_root"

    SIMPLIFICATION = "simplification"

    NUMBER_SERIES = "number_series"


# ============================================================
# Number Series Types
# ============================================================

class SeriesType(str, Enum):

    ARITHMETIC = "arithmetic"

    GEOMETRIC = "geometric"

    FIBONACCI = "fibonacci"

    SQUARES = "squares"

    CUBES = "cubes"

    PRIMES = "primes"

    DIFFERENCE = "difference"

    ALTERNATE = "alternate"

    MIXED = "mixed"


# ============================================================
# PDF Sections
# ============================================================

class PDFSection(str, Enum):

    SQUARES = "Squares"

    CUBES = "Cubes"

    SQUARE_ROOTS = "Square Roots"

    CUBE_ROOTS = "Cube Roots"

    SIMPLIFICATION = "Simplification"

    NUMBER_SERIES = "Missing Number Series"


# ============================================================
# PDF Theme
# ============================================================

class PDFTheme(str, Enum):

    CLASSIC = "classic"

    MINIMAL = "minimal"

    MODERN = "modern"


# ============================================================
# Email Status
# ============================================================

class EmailStatus(str, Enum):

    SUCCESS = "success"

    FAILED = "failed"


# ============================================================
# Generation Status
# ============================================================

class GenerationStatus(str, Enum):

    SUCCESS = "success"

    FAILED = "failed"


# ============================================================
# History Action
# ============================================================

class HistoryAction(str, Enum):

    CREATED = "created"

    DUPLICATE = "duplicate"

    REMOVED = "removed"


# ============================================================
# Log Level
# ============================================================

class LogLevel(str, Enum):

    INFO = "info"

    WARNING = "warning"

    ERROR = "error"

    DEBUG = "debug"