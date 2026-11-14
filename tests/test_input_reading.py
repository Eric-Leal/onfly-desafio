"""Testes adicionais: leitura completa do arquivo de reservas."""

import json

from cli_runner import DATA_DIR, RATES, run_cli_raw
from helpers import run_cli


def test_reads_every_row_beyond_200(tmp_path):
    """Nenhuma reserva é descartada, mesmo acima de 200 linhas."""
    report = run_cli(tmp_path, [{"reservation_id": f"R-{i}"} for i in range(250)])
    assert report["summary"]["total_reservations"] == 250
    assert report["summary"]["total_amount_brl"] == "25000.00"


def test_full_dataset_reads_all_rows(tmp_path):
    """O dataset fornecido tem 300 reservas e o JSON segue o schema."""
    output = tmp_path / "report.json"
    process = run_cli_raw(
        "--input", str(DATA_DIR / "reservas_hoteis.csv"), "--rates", str(RATES), "--output", str(output)
    )
    assert process.returncode == 0, process.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["summary"]["total_reservations"] == 300
    assert set(report) == {"report_version", "generated_at", "summary", "by_month", "top_hotels"}
