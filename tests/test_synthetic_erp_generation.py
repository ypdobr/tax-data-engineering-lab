from pathlib import Path

from tax_data_lab.canonical_model import build_canonical_transactions, validate_transactions
from tax_data_lab.data_generation.generate_synthetic_erp import generate
from tax_data_lab.reporting_shapes import build_intercompany_review_shape


def read_header(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()[0].split(",")


def test_generator_creates_expected_tables(tmp_path: Path) -> None:
    generate(tmp_path, seed=7, transaction_count=10)

    expected = {
        "entities.csv",
        "counterparties.csv",
        "products.csv",
        "fx_rates.csv",
        "invoices.csv",
        "invoice_lines.csv",
    }
    assert {path.name for path in tmp_path.iterdir()} == expected


def test_invoice_schema_is_stable(tmp_path: Path) -> None:
    generate(tmp_path, seed=7, transaction_count=10)

    assert read_header(tmp_path / "invoices.csv") == [
        "invoice_id",
        "entity_id",
        "counterparty_id",
        "invoice_date",
        "period",
        "currency",
        "total_amount",
        "source_system",
    ]


def test_canonical_model_creates_reviewable_transactions(tmp_path: Path) -> None:
    generate(tmp_path, seed=7, transaction_count=10)

    rows = build_canonical_transactions(tmp_path)

    assert rows
    assert "transaction_id" in rows[0]
    assert "amount_eur" in rows[0]
    assert "source_reference" in rows[0]


def test_validation_rules_return_review_queue(tmp_path: Path) -> None:
    generate(tmp_path, seed=7, transaction_count=10)
    rows = build_canonical_transactions(tmp_path)

    exceptions = validate_transactions(rows)

    assert isinstance(exceptions, list)
    assert all("rule_id" in item for item in exceptions)


def test_intercompany_review_shape_aggregates_group_transactions(tmp_path: Path) -> None:
    generate(tmp_path, seed=7, transaction_count=30)
    canonical = build_canonical_transactions(tmp_path)

    review_rows = build_intercompany_review_shape(canonical)

    assert review_rows
    assert all(row["relationship_type"] == "group" for row in review_rows)
    assert all("review_flag" in row for row in review_rows)
