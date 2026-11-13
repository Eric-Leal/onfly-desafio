"""Testes adicionais: cenários das regras de negócio não cobertos pelos testes fornecidos."""

from helpers import run_cli


def test_reads_every_row_beyond_200(tmp_path):
    rows = [{"reservation_id": f"R-{i}"} for i in range(250)]
    report = run_cli(tmp_path, rows)
    assert report["summary"]["total_reservations"] == 250
    assert report["summary"]["total_room_nights"] == 250
    assert report["summary"]["total_amount_brl"] == "25000.00"


def test_nights_across_year_boundary_use_checkin_month(tmp_path):
    report = run_cli(
        tmp_path,
        [{"checkin_date": "2024-12-30", "checkout_date": "2025-01-02"}],
    )
    assert report["summary"]["total_room_nights"] == 3
    assert [month["month"] for month in report["by_month"]] == ["2024-12"]


def test_nights_multiply_by_rooms(tmp_path):
    report = run_cli(
        tmp_path,
        [{"checkin_date": "2025-01-10", "checkout_date": "2025-01-13", "rooms": "3"}],
    )
    assert report["summary"]["total_room_nights"] == 9


def test_non_confirmed_stay_out_of_by_month_and_top_hotels(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "checkin_date": "2025-01-10", "checkout_date": "2025-01-11"},
            {"reservation_id": "R-2", "hotel_id": "H02", "status": "CANCELLED", "checkin_date": "2025-02-10",
             "checkout_date": "2025-02-11", "amount": "9000.00"},
            {"reservation_id": "R-3", "hotel_id": "H03", "status": "NO_SHOW", "checkin_date": "2025-03-10",
             "checkout_date": "2025-03-11", "amount": "9000.00"},
        ],
    )
    assert [month["month"] for month in report["by_month"]] == ["2025-01"]
    assert report["by_month"][0]["reservations"] == 1
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01"]


def test_only_cancelled_yields_zero_average_and_empty_lists(tmp_path):
    report = run_cli(tmp_path, [{"status": "CANCELLED"}])
    assert report["summary"]["total_room_nights"] == 0
    assert report["summary"]["total_amount_brl"] == "0.00"
    assert report["summary"]["average_nightly_rate_brl"] == "0.00"
    assert report["by_month"] == []
    assert report["top_hotels"] == []


def test_top_hotels_tie_breaks_by_hotel_id_ascending(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H03", "amount": "500.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "amount": "500.00"},
            {"reservation_id": "R-3", "hotel_id": "H02", "amount": "500.00"},
        ],
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02", "H03"]


def test_top_hotels_aggregates_same_hotel_and_respects_top(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "amount": "100.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "amount": "100.00"},
            {"reservation_id": "R-3", "hotel_id": "H02", "amount": "150.00"},
        ],
        top=1,
    )
    assert report["top_hotels"] == [
        {"hotel_id": "H01", "hotel_name": "Hotel Teste", "room_nights": 2, "total_brl": "200.00"}
    ]


def test_rounds_half_up_on_serialization(tmp_path):
    # 0.75 USD * 5.42 = 4.065 -> half-up 4.07 (half-even daria 4.06)
    report = run_cli(tmp_path, [{"currency": "USD", "amount": "0.75"}])
    assert report["summary"]["total_amount_brl"] == "4.07"


def test_sums_exact_values_and_rounds_only_at_the_end(tmp_path):
    # 0.25 USD * 5.42 = 1.355; somar exato dá 2.71, arredondar por linha daria 2.72
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "currency": "USD", "amount": "0.25"},
            {"reservation_id": "R-2", "currency": "USD", "amount": "0.25"},
        ],
    )
    assert report["summary"]["total_amount_brl"] == "2.71"


def test_eur_conversion_multiplies_by_rate(tmp_path):
    report = run_cli(tmp_path, [{"currency": "EUR", "amount": "150.00"}])
    assert report["summary"]["total_amount_brl"] == "882.00"
