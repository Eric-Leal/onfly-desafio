"""Testes adicionais: status não faturáveis fora das quebras por mês e hotel."""

from helpers import run_cli


def test_non_confirmed_stay_out_of_by_month_and_top_hotels(tmp_path):
    """CANCELLED e NO_SHOW não entram em by_month nem em top_hotels."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01"},
            {"reservation_id": "R-2", "hotel_id": "H02", "status": "CANCELLED", "checkin_date": "2025-02-10",
             "checkout_date": "2025-02-11", "amount": "9000.00"},
            {"reservation_id": "R-3", "hotel_id": "H03", "status": "NO_SHOW", "checkin_date": "2025-03-10",
             "checkout_date": "2025-03-11", "amount": "9000.00"},
        ],
    )
    assert [(m["month"], m["reservations"]) for m in report["by_month"]] == [("2025-01", 1)]
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01"]


def test_only_cancelled_yields_zero_average_and_empty_lists(tmp_path):
    """Sem noites faturáveis, a média é "0.00" e as quebras ficam vazias."""
    report = run_cli(tmp_path, [{"status": "CANCELLED"}])
    assert report["summary"]["average_nightly_rate_brl"] == "0.00"
    assert report["by_month"] == []
    assert report["top_hotels"] == []
