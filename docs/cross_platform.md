# Cross-platform notes (local dev)

- **Paths**: The stack uses `pathlib`; `validate-env` prints **resolved** absolute paths. On **Windows**, JSON may show mixed drive-letter casing — this is normal.
- **Environment variables**: In PowerShell, quote paths with spaces. You may use forward slashes in `.env` values on Windows.
- **Line endings**: Repository uses LF; Git `core.autocrlf` on Windows is usually fine for Python.
- **CI**: Linux paths are the reference; `bootstrap-dev-snapshot` + `pytest` should pass on macOS/Windows with Python 3.11+ and `pip install -e ".[dev]"`.
