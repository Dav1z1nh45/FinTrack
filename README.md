# FinTrack

A simple personal income and expense tracker built with Python, Streamlit, Pandas, and SQLite.

## Features

- Record income and expenses with categories, dates, and optional notes.
- View income, expenses, and balance for a selected period.
- Visualize expenses by category and monthly income/expense movement.
- Filter transactions by type and category.
- Export filtered transactions to CSV.
- Delete transactions with a confirmation step.
- Store data locally in SQLite.

## Requirements

- Python 3.10 or newer
- pip

## Run locally

1. Clone or download this repository.
2. Open a terminal in the project folder.
3. Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

5. Start the application:

```bash
streamlit run app.py
```

Streamlit will print a local address to open in your browser.

## Data and privacy

The SQLite database (`fintrack.db`) is created automatically in the project folder. It is excluded from Git by `.gitignore`. Your data stays local unless you deliberately share the database or deploy the app with a database setup appropriate for that environment.

## Run tests

```bash
python -m pytest
```

## Tech stack

- Python
- Streamlit
- SQLite
- Pandas
- Pytest

## Disclaimer

FinTrack is an educational project for tracking records. It does not provide financial advice.
