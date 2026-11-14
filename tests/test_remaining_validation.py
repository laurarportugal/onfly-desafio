"""Regression tests for invalid input and CLI edge cases."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from helpers import BASE, COLUMNS

from onfly_report.cli import main
from onfly_report.exceptions import InputFileError
from onfly_report.models import RawRow
from onfly_report.repositories.csv_rate_repository import CsvRateRepository
from onfly_report.repositories.csv_reservation_repository import CsvReservationRepository
from onfly_report.services.currency_converter import convert_to_brl
from onfly_report.services.report_builder import ReportBuilder
from onfly_report.services.row_parser import RowParser


@pytest.mark.parametrize("amount", ["NaN", "Infinity", "-Infinity"])
def test_row_parser_rejects_non_finite_amounts(amount: str):
    values = {**BASE, "amount": amount}
    with pytest.raises(InputFileError):
        RowParser().parse(RawRow(line_number=2, values=values))


@pytest.mark.parametrize("rate", ["NaN", "Infinity", "-Infinity"])
def test_rate_repository_rejects_non_finite_rates(tmp_path, rate: str):
    rates_path = tmp_path / "rates.csv"
    rates_path.write_text(f"currency,rate_to_brl\nUSD,{rate}\n", encoding="utf-8")

    with pytest.raises(InputFileError):
        CsvRateRepository(rates_path).read()


def test_reservation_repository_currently_accepts_header_only_csv(tmp_path):
    input_path = tmp_path / "reservations.csv"
    input_path.write_text(",".join(COLUMNS) + "\n", encoding="utf-8")

    assert CsvReservationRepository(input_path).read() == []


def test_rate_repository_rejects_duplicate_currency(tmp_path):
    rates_path = tmp_path / "rates.csv"
    rates_path.write_text(
        "currency,rate_to_brl\nUSD,2\nUSD,3\n",
        encoding="utf-8",
    )

    with pytest.raises(InputFileError, match="duplicada"):
        CsvRateRepository(rates_path).read()


def test_currency_converter_reports_missing_rate_as_input_error():
    with pytest.raises(InputFileError):
        convert_to_brl(Decimal("10"), "USD", {"BRL": Decimal("1")})


def test_reservation_repository_reports_invalid_utf8_as_input_error(tmp_path):
    input_path = tmp_path / "reservations.csv"
    input_path.write_bytes(b"reservation_id,hotel_name\nR-1,\xff\n")

    with pytest.raises(InputFileError):
        CsvReservationRepository(input_path).read()


def test_row_parser_rejects_unknown_status():
    values = {**BASE, "status": "PENDING"}
    with pytest.raises(InputFileError):
        RowParser().parse(RawRow(line_number=2, values=values))


def test_row_parser_currently_accepts_zero_night_stay():
    values = {**BASE, "checkout_date": BASE["checkin_date"]}

    reservation = RowParser().parse(RawRow(line_number=2, values=values))

    assert reservation.checkout == reservation.checkin


def test_builder_rejects_different_names_for_same_hotel_id():
    rows = [
        RawRow(line_number=2, values={**BASE, "hotel_name": "Name A"}),
        RawRow(line_number=3, values={**BASE, "hotel_name": "Name B"}),
    ]

    class Reservations:
        def read(self):
            return rows

    class Rates:
        def read(self):
            return {"BRL": Decimal("1")}

    with pytest.raises(InputFileError, match="linha 3"):
        ReportBuilder(Reservations(), Rates()).build()


def test_builder_checks_hotel_name_consistency_across_all_statuses():
    rows = [
        RawRow(line_number=2, values={**BASE, "hotel_name": "Name A", "status": "CONFIRMED"}),
        RawRow(line_number=3, values={**BASE, "hotel_name": "Name B", "status": "CANCELLED"}),
    ]

    class Reservations:
        def read(self):
            return rows

    class Rates:
        def read(self):
            return {"BRL": Decimal("1")}

    with pytest.raises(InputFileError, match="linha 3"):
        ReportBuilder(Reservations(), Rates()).build()


def test_builder_normalizes_generated_at_to_fixed_minus_three_offset():
    class EmptyReservations:
        def read(self):
            return []

    class EmptyRates:
        def read(self):
            return {"BRL": Decimal("1")}

    report = ReportBuilder(
        reservation_repository=EmptyReservations(),
        rate_repository=EmptyRates(),
        now=datetime(2025, 1, 1, tzinfo=timezone.utc),
    ).build()

    assert report["generated_at"] == "2024-12-31T21:00:00-03:00"


def test_cli_refuses_to_overwrite_reservation_input(tmp_path):
    input_path = tmp_path / "reservations.csv"
    rates_path = tmp_path / "rates.csv"
    with input_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerow(BASE)
    rates_path.write_text("currency,rate_to_brl\nBRL,1\n", encoding="utf-8")

    original_content = input_path.read_text(encoding="utf-8")
    exit_code = main(
        [
            "--input",
            str(input_path),
            "--rates",
            str(rates_path),
            "--output",
            str(input_path),
        ]
    )

    assert exit_code == 2
    assert input_path.read_text(encoding="utf-8") == original_content
