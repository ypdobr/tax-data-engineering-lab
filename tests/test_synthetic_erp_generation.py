from pathlib import Path

from tax_data_lab.data_generation.generate_synthetic_erp import generate


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

