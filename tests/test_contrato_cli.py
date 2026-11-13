"""Testes adicionais: contrato do CLI (amostra de validação, schema e códigos de saída)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _run(*args: str) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src") + os.pathsep + environment.get("PYTHONPATH", "")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "onfly_report", *args],
        cwd=str(PROJECT_ROOT),
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_validation_sample_matches_readme(tmp_path):
    output = tmp_path / "exemplo.json"
    process = _run(
        "--input", str(DATA_DIR / "exemplo-validacao.csv"),
        "--rates", str(DATA_DIR / "taxas_cambio.csv"),
        "--output", str(output),
    )
    assert process.returncode == 0, process.stderr
    report = json.loads(output.read_text(encoding="utf-8"))

    assert report["report_version"] == "1.0"
    assert report["generated_at"].endswith("-03:00")
    assert report["summary"] == {
        "total_reservations": 12,
        "confirmed_reservations": 9,
        "cancelled_reservations": 2,
        "no_show_reservations": 1,
        "total_room_nights": 28,
        "total_amount_brl": "7566.00",
        "average_nightly_rate_brl": "270.21",
    }
    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 8, "room_nights": 25, "total_brl": "6684.00"},
        {"month": "2025-02", "reservations": 1, "room_nights": 3, "total_brl": "882.00"},
    ]
    assert report["top_hotels"] == [
        {"hotel_id": "H01", "hotel_name": "Hotel Aurora Paulista", "room_nights": 3, "total_brl": "1200.00"},
        {"hotel_id": "H02", "hotel_name": "Hotel Mirante", "room_nights": 2, "total_brl": "1084.00"},
        {"hotel_id": "H12", "hotel_name": "Hotel Miami Beach", "room_nights": 1, "total_brl": "1000.00"},
        {"hotel_id": "H10", "hotel_name": "Hotel Madrid, Gran Vía", "room_nights": 4, "total_brl": "900.00"},
        {"hotel_id": "H09", "hotel_name": "Hotel Lisboa, Centro", "room_nights": 3, "total_brl": "882.00"},
    ]


def test_full_dataset_reads_all_rows(tmp_path):
    output = tmp_path / "report.json"
    process = _run(
        "--input", str(DATA_DIR / "reservas_hoteis.csv"),
        "--rates", str(DATA_DIR / "taxas_cambio.csv"),
        "--output", str(output),
    )
    assert process.returncode == 0, process.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["summary"]["total_reservations"] == 300
    assert set(report) == {"report_version", "generated_at", "summary", "by_month", "top_hotels"}
    assert len(report["top_hotels"]) == 5


def test_missing_input_exits_2(tmp_path):
    process = _run(
        "--input", str(tmp_path / "nao-existe.csv"),
        "--rates", str(DATA_DIR / "taxas_cambio.csv"),
        "--output", str(tmp_path / "report.json"),
    )
    assert process.returncode == 2


def test_top_below_one_exits_2(tmp_path):
    process = _run(
        "--input", str(DATA_DIR / "exemplo-validacao.csv"),
        "--rates", str(DATA_DIR / "taxas_cambio.csv"),
        "--output", str(tmp_path / "report.json"),
        "--top", "0",
    )
    assert process.returncode == 2


def test_currency_without_rate_exits_2(tmp_path):
    rates = tmp_path / "rates.csv"
    rates.write_text("currency,rate_to_brl\nBRL,1.000000\n", encoding="utf-8")
    process = _run(
        "--input", str(DATA_DIR / "exemplo-validacao.csv"),
        "--rates", str(rates),
        "--output", str(tmp_path / "report.json"),
    )
    assert process.returncode == 2
