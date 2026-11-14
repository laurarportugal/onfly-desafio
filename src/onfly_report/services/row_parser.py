"""Conversão de uma linha do CSV para o modelo de reserva."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation

from ..exceptions import InputFileError
from ..models import RawRow, Reservation


class RowParser:
    """Converte a linha crua em Reservation.

    O arquivo de entrada é consistente; falhas de formato são erro de arquivo, não dado a
    ser descartado.
    """

    REQUIRED_TEXT_FIELDS = (
        "reservation_id",
        "hotel_id",
        "hotel_name",
        "status",
        "currency",
    )
    VALID_STATUSES = {"CONFIRMED", "CANCELLED", "NO_SHOW"}

    def parse(self, raw: RawRow) -> Reservation:
        values = raw.values
        try:
            text_values = {
                field: (values.get(field) or "").strip()
                for field in (
                    "reservation_id",
                    "traveler_name",
                    "company_id",
                    "hotel_id",
                    "hotel_name",
                    "city",
                    "country",
                    "status",
                    "currency",
                    "payment_method",
                )
            }
            checkin_text = (values.get("checkin_date") or "").strip()
            checkout_text = (values.get("checkout_date") or "").strip()
            for field, date_text in (
                ("checkin_date", checkin_text),
                ("checkout_date", checkout_text),
            ):
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text) is None:
                    raise InputFileError(
                        f"linha {raw.line_number}: {field} deve seguir o formato YYYY-MM-DD"
                    )

            checkin = date.fromisoformat(checkin_text)
            checkout = date.fromisoformat(checkout_text)
            rooms = int((values.get("rooms") or "").strip())
            amount = Decimal((values.get("amount") or "").strip())
        except InputFileError:
            raise
        except (ValueError, InvalidOperation) as err:
            raise InputFileError(f"linha {raw.line_number} invalida: {err}") from err

        for field in self.REQUIRED_TEXT_FIELDS:
            if not text_values[field]:
                raise InputFileError(
                    f"linha {raw.line_number}: campo obrigatorio vazio: {field}"
                )

        if text_values["status"] not in self.VALID_STATUSES:
            raise InputFileError(
                f"linha {raw.line_number}: status invalido: {text_values['status']}"
            )

        if rooms <= 0:
            raise InputFileError(
                f"linha {raw.line_number}: rooms deve ser maior que zero"
            )
        if not amount.is_finite():
            raise InputFileError(
                f"linha {raw.line_number}: amount deve ser um valor decimal finito"
            )
        if checkout < checkin:
            raise InputFileError(
                f"linha {raw.line_number}: checkout_date nao pode ser anterior a checkin_date"
            )

        return Reservation(
            reservation_id=text_values["reservation_id"],
            traveler_name=text_values["traveler_name"],
            company_id=text_values["company_id"],
            hotel_id=text_values["hotel_id"],
            hotel_name=text_values["hotel_name"],
            city=text_values["city"],
            country=text_values["country"],
            checkin=checkin,
            checkout=checkout,
            rooms=rooms,
            status=text_values["status"],
            currency=text_values["currency"],
            amount=amount,
            payment_method=text_values["payment_method"],
            line_number=raw.line_number,
        )
