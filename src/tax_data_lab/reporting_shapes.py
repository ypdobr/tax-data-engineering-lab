from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        rows = [
            {
                "period": "",
                "entity_id": "",
                "counterparty_id": "",
                "relationship_type": "",
                "transaction_count": 0,
                "gross_amount_eur": 0,
                "absolute_amount_eur": 0,
                "tax_codes": "",
                "commodity_codes": "",
                "review_flag": "",
            }
        ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def to_float(value: object) -> float:
    if value in ("", None):
        return 0.0
    return float(value)


def build_intercompany_review_shape(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], dict[str, object]] = {}
    tax_codes: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    commodity_codes: dict[tuple[str, str, str], set[str]] = defaultdict(set)

    for row in rows:
        if row.get("relationship_type") != "group":
            continue

        key = (row["period"], row["entity_id"], row["counterparty_id"])
        if key not in grouped:
            grouped[key] = {
                "period": row["period"],
                "entity_id": row["entity_id"],
                "counterparty_id": row["counterparty_id"],
                "relationship_type": row["relationship_type"],
                "transaction_count": 0,
                "gross_amount_eur": 0.0,
                "absolute_amount_eur": 0.0,
                "tax_codes": "",
                "commodity_codes": "",
                "review_flag": "",
            }

        amount_eur = to_float(row.get("amount_eur"))
        grouped[key]["transaction_count"] = int(grouped[key]["transaction_count"]) + 1
        grouped[key]["gross_amount_eur"] = round(float(grouped[key]["gross_amount_eur"]) + amount_eur, 2)
        grouped[key]["absolute_amount_eur"] = round(float(grouped[key]["absolute_amount_eur"]) + abs(amount_eur), 2)
        tax_codes[key].add(row.get("tax_code", ""))
        commodity_codes[key].add(row.get("commodity_code", ""))

    output: list[dict[str, object]] = []
    for key, item in grouped.items():
        item["tax_codes"] = ";".join(sorted(code for code in tax_codes[key] if code))
        item["commodity_codes"] = ";".join(sorted(code for code in commodity_codes[key] if code))
        item["review_flag"] = classify_review_flag(item)
        output.append(item)

    return sorted(output, key=lambda row: (str(row["period"]), str(row["entity_id"]), str(row["counterparty_id"])))


def classify_review_flag(row: dict[str, object]) -> str:
    transaction_count = int(row["transaction_count"])
    absolute_amount = float(row["absolute_amount_eur"])
    gross_amount = float(row["gross_amount_eur"])

    flags = []
    if absolute_amount >= 500000:
        flags.append("high_value")
    if transaction_count >= 10:
        flags.append("high_volume")
    if gross_amount < 0:
        flags.append("net_credit_position")
    return ";".join(flags) if flags else "standard_review"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build generic reporting shapes from canonical transactions.")
    parser.add_argument(
        "--canonical-file",
        default="data/processed/canonical_transactions.csv",
        help="Canonical transaction CSV file.",
    )
    parser.add_argument("--output-dir", default="data/reporting", help="Output folder for reporting shapes.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    canonical_rows = read_csv(Path(args.canonical_file))
    output_dir = Path(args.output_dir)
    intercompany = build_intercompany_review_shape(canonical_rows)
    write_csv(output_dir / "intercompany_transaction_review.csv", intercompany)


if __name__ == "__main__":
    main()

