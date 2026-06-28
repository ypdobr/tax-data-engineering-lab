from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def index_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def build_canonical_transactions(input_dir: Path) -> list[dict[str, object]]:
    entities = index_by(read_csv(input_dir / "entities.csv"), "entity_id")
    counterparties = index_by(read_csv(input_dir / "counterparties.csv"), "counterparty_id")
    products = index_by(read_csv(input_dir / "products.csv"), "product_id")
    invoices = index_by(read_csv(input_dir / "invoices.csv"), "invoice_id")
    fx_rates = {
        (row["period"], row["currency"]): float(row["rate_to_eur"])
        for row in read_csv(input_dir / "fx_rates.csv")
    }
    invoice_lines = read_csv(input_dir / "invoice_lines.csv")

    rows: list[dict[str, object]] = []
    for line in invoice_lines:
        invoice = invoices.get(line["invoice_id"], {})
        entity = entities.get(invoice.get("entity_id", ""), {})
        counterparty = counterparties.get(invoice.get("counterparty_id", ""), {})
        product = products.get(line["product_id"], {})
        amount = float(line["amount"])
        period = invoice.get("period", "")
        currency = line["currency"]
        fx_rate = fx_rates.get((period, currency))
        amount_eur = round(amount * fx_rate, 2) if fx_rate else ""

        rows.append(
            {
                "transaction_id": f"{line['invoice_id']}-{line['line_no']}",
                "period": period,
                "entity_id": invoice.get("entity_id", ""),
                "entity_country": entity.get("country", ""),
                "counterparty_id": invoice.get("counterparty_id", ""),
                "counterparty_country": counterparty.get("country", ""),
                "relationship_type": counterparty.get("relationship_type", ""),
                "product_id": line["product_id"],
                "product_category": product.get("category", ""),
                "commodity_code": product.get("commodity_code", ""),
                "account": line["account"],
                "tax_code": line["tax_code"],
                "amount": round(amount, 2),
                "currency": currency,
                "fx_rate_to_eur": fx_rate if fx_rate else "",
                "amount_eur": amount_eur,
                "source_system": invoice.get("source_system", ""),
                "source_reference": line["source_reference"],
            }
        )
    return rows


def validate_transactions(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    allowed_tax_codes = {"STD", "RED", "EXM", "RC", "IMP"}
    seen_references: set[str] = set()
    exceptions: list[dict[str, object]] = []

    for row in rows:
        checks = []
        if not row["entity_id"]:
            checks.append("missing_entity")
        if not row["counterparty_id"]:
            checks.append("missing_counterparty")
        if row["currency"] and not row["fx_rate_to_eur"]:
            checks.append("missing_fx_rate")
        if row["tax_code"] not in allowed_tax_codes:
            checks.append("invalid_tax_code")
        if row["source_reference"] in seen_references:
            checks.append("duplicate_source_reference")
        seen_references.add(str(row["source_reference"]))
        if row["relationship_type"] == "group" and row["entity_country"] == row["counterparty_country"]:
            checks.append("domestic_group_transaction")
        if float(row["amount"]) < 0:
            checks.append("negative_amount_review")

        for check in checks:
            exceptions.append(
                {
                    "transaction_id": row["transaction_id"],
                    "period": row["period"],
                    "rule_id": check,
                    "severity": "review",
                    "source_reference": row["source_reference"],
                }
            )

    return exceptions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical transactions and validation exceptions.")
    parser.add_argument("--input-dir", default="data/synthetic_erp", help="Folder with synthetic source CSV files.")
    parser.add_argument("--output-dir", default="data/processed", help="Output folder for processed CSV files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    canonical = build_canonical_transactions(input_dir)
    exceptions = validate_transactions(canonical)
    write_csv(output_dir / "canonical_transactions.csv", canonical)
    if exceptions:
        write_csv(output_dir / "validation_exceptions.csv", exceptions)
    else:
        write_csv(
            output_dir / "validation_exceptions.csv",
            [{"transaction_id": "", "period": "", "rule_id": "", "severity": "", "source_reference": ""}],
        )


if __name__ == "__main__":
    main()

