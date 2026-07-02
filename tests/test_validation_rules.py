"""Deterministic tests for the canonical model and validation rule engine.

The generator-based tests exercise the pipeline with random synthetic data.
These tests use hand-crafted source tables instead, so every validation rule
in ``validate_transactions`` is pinned to a known input and expected outcome.
"""

from __future__ import annotations

import csv
from pathlib import Path

from tax_data_lab.canonical_model import build_canonical_transactions, validate_transactions


def write_table(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_source_tables(
    base: Path,
    invoices: list[dict[str, object]],
    invoice_lines: list[dict[str, object]],
) -> None:
    write_table(
        base / "entities.csv",
        ["entity_id", "country"],
        [
            {"entity_id": "E1", "country": "DE"},
            {"entity_id": "E2", "country": "PL"},
        ],
    )
    write_table(
        base / "counterparties.csv",
        ["counterparty_id", "country", "relationship_type"],
        [
            {"counterparty_id": "C1", "country": "PL", "relationship_type": "group"},
            {"counterparty_id": "C2", "country": "DE", "relationship_type": "group"},
            {"counterparty_id": "C3", "country": "FR", "relationship_type": "external"},
        ],
    )
    write_table(
        base / "products.csv",
        ["product_id", "category", "commodity_code"],
        [{"product_id": "P1", "category": "hardware", "commodity_code": "8471"}],
    )
    write_table(
        base / "fx_rates.csv",
        ["period", "currency", "rate_to_eur"],
        [
            {"period": "2026-01", "currency": "USD", "rate_to_eur": "0.9"},
            {"period": "2026-01", "currency": "EUR", "rate_to_eur": "1.0"},
        ],
    )
    write_table(
        base / "invoices.csv",
        [
            "invoice_id",
            "entity_id",
            "counterparty_id",
            "invoice_date",
            "period",
            "currency",
            "total_amount",
            "source_system",
        ],
        invoices,
    )
    write_table(
        base / "invoice_lines.csv",
        [
            "invoice_id",
            "line_no",
            "product_id",
            "amount",
            "currency",
            "account",
            "tax_code",
            "source_reference",
        ],
        invoice_lines,
    )


def make_invoice(
    invoice_id: str,
    entity_id: str = "E1",
    counterparty_id: str = "C1",
) -> dict[str, object]:
    return {
        "invoice_id": invoice_id,
        "entity_id": entity_id,
        "counterparty_id": counterparty_id,
        "invoice_date": "2026-01-15",
        "period": "2026-01",
        "currency": "USD",
        "total_amount": "100.00",
        "source_system": "ERP-A",
    }


def make_line(invoice_id: str, line_no: int, **overrides: object) -> dict[str, object]:
    line: dict[str, object] = {
        "invoice_id": invoice_id,
        "line_no": line_no,
        "product_id": "P1",
        "amount": "100.00",
        "currency": "USD",
        "account": "400000",
        "tax_code": "STD",
        "source_reference": f"REF-{invoice_id}-{line_no}",
    }
    line.update(overrides)
    return line


def rules_by_transaction(exceptions: list[dict[str, object]]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for item in exceptions:
        result.setdefault(str(item["transaction_id"]), set()).add(str(item["rule_id"]))
    return result


def test_canonical_join_and_eur_conversion(tmp_path: Path) -> None:
    write_source_tables(tmp_path, [make_invoice("INV1")], [make_line("INV1", 1)])

    rows = build_canonical_transactions(tmp_path)

    assert len(rows) == 1
    row = rows[0]
    assert row["transaction_id"] == "INV1-1"
    assert row["entity_country"] == "DE"
    assert row["counterparty_country"] == "PL"
    assert row["relationship_type"] == "group"
    assert row["product_category"] == "hardware"
    assert row["commodity_code"] == "8471"
    assert row["fx_rate_to_eur"] == 0.9
    assert row["amount_eur"] == 90.0
    assert row["source_system"] == "ERP-A"


def test_clean_cross_border_group_transaction_passes_validation(tmp_path: Path) -> None:
    write_source_tables(tmp_path, [make_invoice("INV1")], [make_line("INV1", 1)])

    exceptions = validate_transactions(build_canonical_transactions(tmp_path))

    assert exceptions == []


def test_missing_fx_rate_is_flagged(tmp_path: Path) -> None:
    write_source_tables(tmp_path, [make_invoice("INV1")], [make_line("INV1", 1, currency="GBP")])

    exceptions = validate_transactions(build_canonical_transactions(tmp_path))

    assert rules_by_transaction(exceptions) == {"INV1-1": {"missing_fx_rate"}}


def test_invalid_tax_code_is_flagged(tmp_path: Path) -> None:
    write_source_tables(tmp_path, [make_invoice("INV1")], [make_line("INV1", 1, tax_code="ZZZ")])

    exceptions = validate_transactions(build_canonical_transactions(tmp_path))

    assert rules_by_transaction(exceptions) == {"INV1-1": {"invalid_tax_code"}}


def test_negative_amount_is_flagged_for_review(tmp_path: Path) -> None:
    write_source_tables(tmp_path, [make_invoice("INV1")], [make_line("INV1", 1, amount="-50.00")])

    exceptions = validate_transactions(build_canonical_transactions(tmp_path))

    assert rules_by_transaction(exceptions) == {"INV1-1": {"negative_amount_review"}}


def test_duplicate_source_reference_flags_second_line_only(tmp_path: Path) -> None:
    lines = [
        make_line("INV1", 1, source_reference="REF-DUP"),
        make_line("INV1", 2, source_reference="REF-DUP"),
    ]
    write_source_tables(tmp_path, [make_invoice("INV1")], lines)

    exceptions = validate_transactions(build_canonical_transactions(tmp_path))

    assert rules_by_transaction(exceptions) == {"INV1-2": {"duplicate_source_reference"}}


def test_domestic_group_transaction_is_flagged(tmp_path: Path) -> None:
    write_source_tables(
        tmp_path,
        [make_invoice("INV1", entity_id="E1", counterparty_id="C2")],
        [make_line("INV1", 1)],
    )

    exceptions = validate_transactions(build_canonical_transactions(tmp_path))

    assert rules_by_transaction(exceptions) == {"INV1-1": {"domestic_group_transaction"}}


def test_unknown_invoice_reference_is_fully_flagged(tmp_path: Path) -> None:
    write_source_tables(tmp_path, [make_invoice("INV1")], [make_line("INVX", 1)])

    exceptions = validate_transactions(build_canonical_transactions(tmp_path))

    assert rules_by_transaction(exceptions) == {
        "INVX-1": {"missing_entity", "missing_counterparty", "missing_fx_rate"}
    }


def test_exception_rows_carry_review_severity_and_reference(tmp_path: Path) -> None:
    write_source_tables(tmp_path, [make_invoice("INV1")], [make_line("INV1", 1, tax_code="ZZZ")])

    exceptions = validate_transactions(build_canonical_transactions(tmp_path))

    assert len(exceptions) == 1
    item = exceptions[0]
    assert item["severity"] == "review"
    assert item["period"] == "2026-01"
    assert item["source_reference"] == "REF-INV1-1"
