"""Testes adicionais: desempate e agregação do ranking de hotéis."""

from helpers import run_cli


def test_top_hotels_tie_breaks_by_hotel_id_ascending(tmp_path):
    """Valores iguais são ordenados por hotel_id ascendente."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H03"},
            {"reservation_id": "R-2", "hotel_id": "H01"},
            {"reservation_id": "R-3", "hotel_id": "H02"},
        ],
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02", "H03"]


def test_top_hotels_aggregates_same_hotel_and_respects_top(tmp_path):
    """Reservas do mesmo hotel somam e --top limita o ranking."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01"},
            {"reservation_id": "R-2", "hotel_id": "H01"},
            {"reservation_id": "R-3", "hotel_id": "H02", "amount": "150.00"},
        ],
        top=1,
    )
    assert report["top_hotels"] == [
        {"hotel_id": "H01", "hotel_name": "Hotel Teste", "room_nights": 2, "total_brl": "200.00"}
    ]
