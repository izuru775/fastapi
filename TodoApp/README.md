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
uv run uvicorn main:app --reload
uv run python main.py
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

## Notes

- `uv add` requires a `pyproject.toml` in the current or a parent directory. If you only have a `requirements.txt`, either run `uv init` first, or use the pip-compatible interface instead: `uv pip install <package>`.
- `uv sync` removes packages from `.venv` that aren't declared in `pyproject.toml` — don't run it if you've manually `pip install`ed extras you want to keep untracked.