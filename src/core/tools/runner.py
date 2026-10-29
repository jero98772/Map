import re
import subprocess
import sys
import tempfile

from core.tools.constans import MAP_INTERPRETER, RUN_TIMEOUT

ANSI_COLORS = re.compile(r"\x1b\[[0-9;]*m")


def run_map(source: str) -> str:
    """Run source with the reference MAP interpreter and return what it prints.

    It runs in a separate process so an endless loop is cut off after RUN_TIMEOUT
    seconds instead of blocking the server.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".py", encoding="utf-8") as fh:
        fh.write(source)
        fh.flush()
        try:
            result = subprocess.run(
                [sys.executable, str(MAP_INTERPRETER), fh.name],
                capture_output=True,
                text=True,
                timeout=RUN_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return f"TimeoutError: stopped after {RUN_TIMEOUT} seconds\n"
    return ANSI_COLORS.sub("", result.stdout + result.stderr)
