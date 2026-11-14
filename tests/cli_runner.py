"""Execução do CLI sobre arquivos reais, sem exigir código de saída 0."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RATES = DATA_DIR / "taxas_cambio.csv"


def run_cli_raw(*args: str) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src") + os.pathsep + environment.get("PYTHONPATH", "")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "onfly_report", *args],
        cwd=str(PROJECT_ROOT),
        env=environment,
        capture_output=True,
        encoding="utf-8",
        timeout=60,
    )
