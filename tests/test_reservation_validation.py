"""Validações semânticas das linhas de reservas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from onfly_report.exceptions import InputFileError
from onfly_report.models import RawRow
from onfly_report.services.row_parser import RowParser

BASE = {
    "reservation_id": "R-1",
    "traveler_name": "Pessoa Teste",
    "company_id": "EMP-001",
    "hotel_id": "H01",
    "hotel_name": "Hotel Teste",
    "city": "Sao Paulo",
    "country": "BR",
    "checkin_date": "2025-01-10",
    "checkout_date": "2025-01-11",
    "rooms": "1",
    "status": "CONFIRMED",
    "currency": "BRL",
    "amount": "100.00",
    "payment_method": "CORPORATE_CARD",
    "booked_at": "2025-01-01T10:00:00-03:00",
}


def parse_row(overrides: dict[str, str] | None = None):
    values = {**BASE, **(overrides or {})}
    return RowParser().parse(RawRow(line_number=2, values=values))


@pytest.mark.parametrize("rooms", ["0", "-1"])
def test_rejects_non_positive_room_count(rooms: str):
    with pytest.raises(InputFileError):
        parse_row({"rooms": rooms})


def test_rejects_checkout_before_checkin():
    with pytest.raises(InputFileError):
        parse_row({"checkin_date": "2025-01-12", "checkout_date": "2025-01-11"})


@pytest.mark.parametrize("field", ["checkin_date", "checkout_date"])
@pytest.mark.parametrize("date_value", ["20250110", "2025-W02-5"])
def test_rejects_dates_not_in_yyyy_mm_dd_format(field: str, date_value: str):
    with pytest.raises(InputFileError):
        parse_row({field: date_value})


@pytest.mark.parametrize("field", ["checkin_date", "checkout_date"])
def test_rejects_nonexistent_dates_with_line_number(field: str):
    with pytest.raises(InputFileError, match="linha 2"):
        parse_row({field: "2025-02-30"})


@pytest.mark.parametrize(
    "field",
    ["reservation_id", "hotel_id", "hotel_name", "status", "currency"],
)
def test_rejects_empty_required_text_fields(field: str):
    with pytest.raises(InputFileError):
        parse_row({field: "   "})


def test_accepts_valid_reservation():
    reservation = parse_row()

    assert reservation.checkin == date(2025, 1, 10)
    assert reservation.checkout == date(2025, 1, 11)
    assert reservation.rooms == 1
    assert reservation.amount == Decimal("100.00")
