"""Testes adicionais: noites na virada de ano."""

from helpers import run_cli


def test_nights_across_year_boundary_use_checkin_month(tmp_path):
    """30/12 a 02/01 são 3 noites, agrupadas no mês do check-in."""
    report = run_cli(tmp_path, [{"checkin_date": "2024-12-30", "checkout_date": "2025-01-02"}])
    assert report["summary"]["total_room_nights"] == 3
    assert [month["month"] for month in report["by_month"]] == ["2024-12"]
