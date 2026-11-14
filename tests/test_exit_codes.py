"""Testes adicionais: código de saída 2 para entrada ou argumento inválido."""

import pytest
from cli_runner import DATA_DIR, RATES, run_cli_raw

SAMPLE = DATA_DIR / "exemplo-validacao.csv"


@pytest.mark.parametrize(
    ("input_csv", "rates_csv", "top"),
    [
        (DATA_DIR / "nao-existe.csv", RATES, "5"),
        (SAMPLE, RATES, "0"),
        (SAMPLE, None, "5"),
    ],
    ids=["missing_input", "top_below_one", "currency_without_rate"],
)
def test_invalid_input_exits_2(tmp_path, input_csv, rates_csv, top):
    """Arquivo ausente, --top < 1 e moeda sem taxa saem com código 2."""
    if rates_csv is None:
        rates_csv = tmp_path / "only_brl.csv"
        rates_csv.write_text("currency,rate_to_brl\nBRL,1.000000\n", encoding="utf-8")
    process = run_cli_raw(
        "--input", str(input_csv), "--rates", str(rates_csv), "--top", top,
        "--output", str(tmp_path / "report.json"),
    )
    assert process.returncode == 2, process.stderr
