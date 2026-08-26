# uv Cheatsheet — Creating & Running a Python Project

## 1. Start a new project

```
cd path/to/your/project
uv init
```

Creates `pyproject.toml`, `uv.lock`, a `.venv`, and a starter `main.py`.

`uv init` must be run in the folder that will be your project root — `.venv` and `pyproject.toml` live there. `uv add`/`uv run` only work if run from that folder (or a subfolder of it).

## 2. Add dependencies

```
uv add fastapi sqlalchemy
uv add "fastapi[standard]"      # with extras (uvicorn, jinja2, python-multipart, etc.)
uv add -r requirements.txt      # import an existing requirements.txt
```

Each `uv add` updates `pyproject.toml` and `uv.lock`, and installs into `.venv` automatically. Only list direct dependencies — uv resolves and locks transitive ones for you.

Remove a dependency:

```
uv remove sqlalchemy
```

## 3. Install from an existing project (e.g. after cloning a repo)

If the repo already has a `pyproject.toml` (with or without `uv.lock`), skip `uv init` — just run:

```
uv sync
```

Reads `pyproject.toml` (and `uv.lock` if present) and creates `.venv` with everything installed.

## 4. Run the project

No need to manually activate `.venv` — prefix commands with `uv run`:

```
uvicorn main:app --reload
python main.py
```

If you do want the venv active in your shell (e.g. so your IDE picks it up):

```
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux
```

## 5. Export to requirements.txt (if some other tool needs it)

```
uv export -o requirements.txt
```

## 6. SQLite3 command line

Open (or create) a database file:

```
sqlite3 mydatabase.db
```

This drops you into the `sqlite>` interactive shell. From there:

```sql
.tables                      -- list all tables
.schema users                -- show CREATE TABLE statement for a table
.headers on                  -- show column names in query output
.mode column                 -- pretty-print query results in columns
.mode csv                    -- output results as CSV instead
.output out.csv               -- redirect output to a file (use .output stdout to reset)
.quit                        -- exit the shell
```

Run SQL directly (still inside the shell):

```sql
SELECT * FROM users;
SELECT * FROM users WHERE username = 'sam';
INSERT INTO users (username, email) VALUES ('sam', 'sam@example.com');
DELETE FROM users WHERE id = 3;
```

Run a one-off query without entering the interactive shell:

```
sqlite3 mydatabase.db "SELECT * FROM users;"
```

Run a `.sql` script file against a database:

```
sqlite3 mydatabase.db < schema.sql
```

Dump the whole database to a `.sql` file (useful for backups/version control):

```
sqlite3 mydatabase.db .dump > backup.sql
```

Restore from a dump:

```
sqlite3 newdatabase.db < backup.sql
```

> Note: `sqlite3` here is the standalone SQLite CLI tool, separate from Python's built-in `sqlite3` module (`import sqlite3`) used inside your app code (e.g. via SQLAlchemy's `sqlite:///mydatabase.db` connection string).

## 7. Alembic (database migrations)

Add it to the project like any other dependency, then run it through `uv run` so it uses the project's `.venv`:

```
uv add alembic
alembic init alembic
```

`alembic init alembic` creates an `alembic/` folder (versions live in `alembic/versions/`) plus a top-level `alembic.ini` config file.

### One-time setup

Two things to point at your database before generating migrations:

- In `alembic.ini`, set `sqlalchemy.url` — or better, leave it blank and set it dynamically in `alembic/env.py` (e.g. read from your app's settings/env vars) so you don't hardcode credentials.
- In `alembic/env.py`, set `target_metadata` to your SQLAlchemy models' `Base.metadata` (e.g. `from myapp.models import Base` then `target_metadata = Base.metadata`). This is required for autogenerate to detect model changes.

### Creating migrations

```
alembic revision -m "add users table"                 # empty migration, write it by hand
alembic revision --autogenerate -m "add users table"   # auto-detect model changes vs. db
```

Autogenerate compares `target_metadata` against the current database schema and writes the `upgrade()`/`downgrade()` diff for you — always review the generated file before applying it, it doesn't catch everything (e.g. table/column renames show up as drop+add).

### Applying / reverting migrations

```
alembic upgrade head       # apply all pending migrations
alembic upgrade +1         # apply just the next one
alembic downgrade -1       # revert the last migration
alembic downgrade base     # revert all migrations
alembic downgrade <rev>    # revert/upgrade to a specific revision id
```

### Inspecting state and history

```
alembic current            # show revision the db is currently at
alembic history            # list all migrations, oldest to newest
alembic history --verbose  # same, with full details per revision
alembic show <rev>         # show details of one specific revision
alembic heads              # show head(s) — more than one means branched history
```

### Branches and out-of-band changes

```
alembic merge -m "merge heads" <rev1> <rev2>   # merge two divergent heads into one
alembic stamp head                              # mark db as up to date WITHOUT running migrations
```

`stamp` is useful when the schema was already brought up to date some other way (e.g. restored from a backup that matches `head`) and you just need Alembic's bookkeeping to agree.

> Note: keep `alembic/versions/` in version control alongside your code — migrations are the source of truth for schema history, not just a local artifact.

## Notes

- `uv add` requires a `pyproject.toml` in the current or a parent directory. If you only have a `requirements.txt`, either run `uv init` first, or use the pip-compatible interface instead: `uv pip install <package>`.
- `uv sync` removes packages from `.venv` that aren't declared in `pyproject.toml` — don't run it if you've manually `pip install`ed extras you want to keep untracked.