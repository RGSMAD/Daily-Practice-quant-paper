# Daily Aptitude Generator

A production-quality Python application that automatically generates daily quantitative aptitude practice sheets in PDF format, creates a corresponding answer key, prevents duplicate questions using question history, and emails the PDFs to configured recipients.

The project is designed with a modular architecture, strong typing, object-oriented programming principles, automated testing, and GitHub Actions for scheduled execution.

---

# Features

- Automatic daily aptitude question generation
- Generates separate Practice Questions PDF
- Generates separate Answer Key PDF
- Prevents duplicate questions using history tracking
- Multiple aptitude topics
- Production-quality modular architecture
- Dataclass-based models
- Type hints throughout the project
- Google-style docstrings
- PEP 8 compliant code
- Configurable using `config.yaml`
- Automated email delivery
- Daily execution using GitHub Actions
- Unit tests included

---

# Topics Covered

The generator currently supports:

- Squares
- Cubes
- Square Roots
- Cube Roots
- Simplification
- Missing Number Series

The project is designed so additional aptitude topics can be added with minimal effort.

---

# Technology Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.12 |
| PDF Generation | ReportLab |
| Configuration | YAML |
| Email | SMTP |
| Testing | pytest |
| CI/CD | GitHub Actions |

---

# Project Architecture

```
                config.yaml
                      │
                      ▼
               src/config.py
                      │
                      ▼
               Application Settings
                      │
     ┌────────────────┼────────────────┐
     ▼                ▼                ▼
Generators        PDF Module      Email Module
     │                │                │
     └────────────────┼────────────────┘
                      ▼
              Daily PDF Generation
                      │
                      ▼
                Email Delivery
```

---

# Project Structure

```
daily-aptitude-generator/
│
├── .github/
│   └── workflows/
│       └── daily-pdf.yml
│
├── src/
│   ├── generators/
│   ├── pdf/
│   ├── email/
│   ├── models/
│   ├── utils/
│   ├── config.py
│   ├── generator.py
│   └── main.py
│
├── assets/
│   └── logo.png
│
├── history/
├── logs/
├── output/
│
├── tests/
│
├── requirements.txt
├── config.yaml
├── README.md
├── LICENSE
└── .gitignore
```

---

# Installation

## Clone the repository

```bash
git clone https://github.com/<your-username>/daily-aptitude-generator.git

cd daily-aptitude-generator
```

---

## Create a virtual environment

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

All configurable values are stored inside:

```
config.yaml
```

Configuration includes:

- Application settings
- PDF settings
- Question counts
- Number ranges
- Difficulty distribution
- Email configuration
- History configuration
- Logging configuration

Example:

```yaml
questions:
  square_questions: 10
  cube_questions: 5
  simplification_questions: 15
```

---

# Email Configuration

The application reads credentials from environment variables.

Example:

```
EMAIL_USER

EMAIL_PASSWORD

RECEIVER_EMAIL
```

Never hardcode credentials inside the source code.

---

# Running the Project

Run the application using:

```bash
python -m src.main
```

or

```bash
python src/main.py
```

depending on your environment.

---

# Generated Output

Every execution generates:

```
output/

├── Daily_Practice.pdf

└── Daily_Practice_Answers.pdf
```

If email is configured successfully, both PDFs are automatically sent to the configured recipient.

---

# Configuration Flow

```
config.yaml
        │
        ▼
src/config.py
        │
        ▼
settings
        │
        ▼
Entire Application
```

The rest of the project accesses configuration through:

```python
from src.config import settings
```

without directly reading the YAML file.

---

# GitHub Actions

The project includes a scheduled GitHub Actions workflow that automates the complete aptitude generation process.

Workflow file:

```text
.github/workflows/daily-pdf.yml
```

The workflow performs the following tasks:

1. Checks out the repository.
2. Sets up Python 3.12.
3. Installs project dependencies.
4. Executes the application.
5. Generates:
   - Practice Questions PDF
   - Answer Key PDF
6. Emails both PDFs to the configured recipient.

The workflow can be configured to run:

- Daily
- Weekly
- Monthly
- Manually using **workflow_dispatch**

---

# Testing

Unit tests are located in:

```text
tests/
```

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Generate a coverage report:

```bash
pytest --cov=src
```

Current test modules:

```text
tests/
├── test_generators.py
├── test_pdf.py
└── test_utils.py
```

---

# Project Modules

## Generators

Responsible for generating aptitude questions.

```text
src/generators/
```

Modules include:

- Square Generator
- Cube Generator
- Square Root Generator
- Cube Root Generator
- Simplification Generator
- Missing Number Series Generator
- Question Bank

---

## PDF

Responsible for generating printable PDFs.

```text
src/pdf/
```

Files:

- `question_pdf.py`
- `answer_pdf.py`

---

## Email

Responsible for sending generated PDFs.

```text
src/email/mailer.py
```

---

## Models

Contains all application data models.

```text
src/models/
```

Files:

- `question.py`
- `answer.py`
- `enums.py`

---

## Utilities

Shared helper modules used across the application.

```text
src/utils/
```

Files:

- `constants.py`
- `helpers.py`
- `history.py`
- `logger.py`
- `validator.py`

---

# Logging

Application logs are stored inside:

```text
logs/
```

Example log file:

```text
generator.log
```

Logging helps monitor:

- Question generation
- PDF creation
- Email delivery
- Errors
- Warnings

---

# Question History

Previously generated questions are stored inside:

```text
history/
```

History tracking prevents duplicate questions from being generated across multiple executions.

Retention period is configurable through:

```yaml
history:
  retain_days: 30
```

---

# Output

Generated PDFs are stored inside:

```text
output/
```

Example:

```text
output/
├── Daily_Practice.pdf
└── Daily_Practice_Answers.pdf
```

---

# Code Quality

The project follows modern Python development practices:

- Python 3.12
- Object-Oriented Programming
- Dataclasses
- Type Hints
- Google-style Docstrings
- PEP 8 Compliance
- Modular Architecture
- Separation of Concerns
- Reusable Components

---

# Future Enhancements

Potential future improvements include:

- Additional aptitude topics
- Percentage problems
- Profit and Loss
- Time and Work
- Time, Speed and Distance
- Number System
- Average
- Ratio and Proportion
- Probability
- Permutation and Combination
- Data Interpretation
- Logical Reasoning
- Verbal Ability
- Difficulty-based question generation
- HTML email support
- PDF password protection
- Docker support
- Cloud deployment
- REST API
- Web interface
- Performance analytics
- Question statistics dashboard
- Multi-language support

---

# Contributing

Contributions are welcome.

If you would like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

Please ensure that:

- Code follows PEP 8.
- New features include tests.
- Existing tests continue to pass.
- Code is documented using Google-style docstrings.

---

# License

This project is distributed under the MIT License.

See the `LICENSE` file for complete license details.

---

# Author

**Rajoli Girisai Madhav**

AWS DevOps Engineer | Python | Automation | CI/CD | Cloud Computing

---

# Acknowledgements

This project uses the following open-source technologies:

- Python
- ReportLab
- PyYAML
- pytest
- GitHub Actions

Special thanks to the Python open-source community for providing the libraries and tools that make this project possible.

---

# Support

If you encounter any issues, have suggestions, or would like to contribute, please open an issue or submit a pull request through the project's GitHub repository.

---

## Happy Learning! 📚