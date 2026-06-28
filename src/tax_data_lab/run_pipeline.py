from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from tax_data_lab.canonical_model import build_canonical_transactions, validate_transactions, write_csv
from tax_data_lab.data_generation.generate_synthetic_erp import generate
from tax_data_lab.reporting_shapes import build_intercompany_review_shape


def count_csv_rows(path: Path) -> int:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return max(sum(1 for _ in csv.DictReader(handle)), 0)


def write_manifest(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline(base_dir: Path, transactions: int, seed: int) -> dict[str, object]:
    source_dir = base_dir / "bronze_synthetic_erp"
    processed_dir = base_dir / "silver_processed"
    reporting_dir = base_dir / "gold_reporting"
    monitoring_dir = base_dir / "monitoring"

    generate(source_dir, seed=seed, transaction_count=transactions)

    canonical = build_canonical_transactions(source_dir)
    exceptions = validate_transactions(canonical)
    write_csv(processed_dir / "canonical_transactions.csv", canonical)
    write_csv(
        processed_dir / "validation_exceptions.csv",
        exceptions
        or [{"transaction_id": "", "period": "", "rule_id": "", "severity": "", "source_reference": ""}],
    )

    intercompany = build_intercompany_review_shape([{key: str(value) for key, value in row.items()} for row in canonical])
    write_csv(reporting_dir / "intercompany_transaction_review.csv", intercompany)

    manifest = {
        "run_timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "seed": seed,
        "requested_invoice_count": transactions,
        "bronze_invoices": count_csv_rows(source_dir / "invoices.csv"),
        "bronze_invoice_lines": count_csv_rows(source_dir / "invoice_lines.csv"),
        "silver_canonical_transactions": len(canonical),
        "silver_validation_exceptions": len(exceptions),
        "gold_intercompany_review_rows": len(intercompany),
    }
    write_manifest(monitoring_dir / "run_manifest.csv", [manifest])
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local tax data engineering pipeline.")
    parser.add_argument("--base-dir", default="data/pipeline_run", help="Base output folder for the pipeline run.")
    parser.add_argument("--transactions", type=int, default=250, help="Number of synthetic invoices.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible data.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = run_pipeline(Path(args.base_dir), transactions=args.transactions, seed=args.seed)
    for key, value in manifest.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
