"""
enums.py

Centralized enumerations used throughout the
Daily Aptitude Generator.
"""

from enum import Enum, auto


# ============================================================
# Difficulty
# ============================================================

class Difficulty(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()


# ============================================================
# Question Sections
# ============================================================

class QuestionType(Enum):
    SQUARE = auto()
    CUBE = auto()
    SQUARE_ROOT = auto()
    CUBE_ROOT = auto()
    SIMPLIFICATION = auto()
    NUMBER_SERIES = auto()


# ============================================================
# Number Series Types
# ============================================================

class SeriesType(Enum):
    ARITHMETIC = auto()
    GEOMETRIC = auto()
    FIBONACCI = auto()
    SQUARES = auto()
    CUBES = auto()
    PRIMES = auto()
    DIFFERENCE = auto()
    ALTERNATE = auto()
    MIXED = auto()


# ============================================================
# PDF Sections
# ============================================================

class PDFSection(Enum):
    SQUARES = "Squares"
    CUBES = "Cubes"
    SQUARE_ROOTS = "Square Roots"
    CUBE_ROOTS = "Cube Roots"
    SIMPLIFICATION = "Simplification"
    NUMBER_SERIES = "Missing Number Series"


# ============================================================
# PDF Theme
# ============================================================

class PDFTheme(Enum):
    CLASSIC = auto()
    MINIMAL = auto()
    MODERN = auto()


# ============================================================
# Email Status
# ============================================================

class EmailStatus(Enum):
    SUCCESS = auto()
    FAILED = auto()


# ============================================================
# Generation Status
# ============================================================

class GenerationStatus(Enum):
    SUCCESS = auto()
    FAILED = auto()


# ============================================================
# Log Level
# ============================================================

class LogLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    DEBUG = auto()