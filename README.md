# Lost and Found

A minimal Flask + SQLite campus lost-and-found application.

## Requirements

- Python 3.10+
- Flask 3.x

## Run

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python app.py
```

Open the local Flask address shown in the terminal.

The SQLite database is created automatically at:

`database/lost_and_found.sqlite`

## Scope

The application implements:

1. Reporting lost items.
2. Reporting found items.
3. Searching found reports by description, category, and location.
4. Claiming a found item with identifying information.
5. Basic notification records for possible matches and claim events.

There is no authentication, as specified by the project blueprint.
