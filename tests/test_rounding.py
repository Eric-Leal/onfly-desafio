"""Testes adicionais: exatidão e arredondamento do dinheiro."""

from helpers import run_cli


def test_rounds_half_up_on_serialization(tmp_path):
    """0.75 USD * 5.42 = 4.065 vira "4.07" (half-even daria 4.06)."""
    report = run_cli(tmp_path, [{"currency": "USD", "amount": "0.75"}])
    assert report["summary"]["total_amount_brl"] == "4.07"


def test_sums_exact_values_and_rounds_only_at_the_end(tmp_path):
    """1.355 + 1.355 = 2.71; arredondar por linha daria 2.72."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "currency": "USD", "amount": "0.25"},
            {"reservation_id": "R-2", "currency": "USD", "amount": "0.25"},
        ],
    )
    assert report["summary"]["total_amount_brl"] == "2.71"
