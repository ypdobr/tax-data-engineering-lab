from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


FICTIONAL_COMPANIES = [
    "Northstar Components GmbH",
    "Helvetic Process AG",
    "Baltic Mobility Sp. z o.o.",
    "Danube Industrial s.r.o.",
    "Aster Aviation Ltd.",
    "Solaris Materials BV",
]

COUNTRIES = ["DE", "CH", "PL", "NL", "CZ", "GB"]
CURRENCIES = ["EUR", "CHF", "PLN", "GBP"]
PRODUCT_CATEGORIES = ["components", "services", "machinery", "materials", "logistics"]
TAX_CODES = ["STD", "RED", "EXM", "RC", "IMP"]
ACCOUNTS = ["400000", "410000", "500000", "510000", "600000", "610000"]


@dataclass(frozen=True)
class Entity:
    entity_id: str
    name: str
    country: str
    currency: str


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_entities() -> list[Entity]:
    entities: list[Entity] = []
    for idx, company in enumerate(FICTIONAL_COMPANIES, start=1):
        country = COUNTRIES[(idx - 1) % len(COUNTRIES)]
        currency = "CHF" if country == "CH" else "GBP" if country == "GB" else "EUR"
        entities.append(Entity(f"E{idx:03d}", company, country, currency))
    return entities


def make_counterparties(entities: list[Entity]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for idx, entity in enumerate(entities, start=1):
        rows.append(
            {
                "counterparty_id": f"CP{idx:03d}",
                "counterparty_name": entity.name,
                "country": entity.country,
                "relationship_type": "group",
            }
        )
    for idx in range(1, 9):
        rows.append(
            {
                "counterparty_id": f"CPX{idx:03d}",
                "counterparty_name": f"External Supplier {idx:02d} Ltd.",
                "country": random.choice(COUNTRIES),
                "relationship_type": "third_party",
            }
        )
    return rows


def make_products() -> list[dict[str, str]]:
    return [
        {
            "product_id": f"P{idx:03d}",
            "category": category,
            "description": f"synthetic {category} item {idx}",
            "commodity_code": f"{8400 + idx:04d}",
        }
        for idx, category in enumerate(PRODUCT_CATEGORIES * 3, start=1)
    ]


def make_fx_rates() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    base_date = date(2026, 1, 1)
    rates = {"EUR": 1.0, "CHF": 1.06, "PLN": 0.23, "GBP": 1.17}
    for month in range(6):
        period = base_date + timedelta(days=31 * month)
        for currency, rate in rates.items():
            rows.append(
                {
                    "period": period.strftime("%Y-%m"),
                    "currency": currency,
                    "rate_to_eur": round(rate * random.uniform(0.98, 1.02), 4),
                }
            )
    return rows


def make_transactions(
    entities: list[Entity],
    counterparties: list[dict[str, str]],
    products: list[dict[str, str]],
    transaction_count: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    invoices: list[dict[str, object]] = []
    invoice_lines: list[dict[str, object]] = []
    start = date(2026, 1, 1)

    for idx in range(1, transaction_count + 1):
        entity = random.choice(entities)
        counterparty = random.choice(counterparties)
        invoice_id = f"INV{idx:06d}"
        invoice_date = start + timedelta(days=random.randint(0, 179))
        currency = entity.currency if random.random() > 0.25 else random.choice(CURRENCIES)
        line_count = random.randint(1, 4)
        total_amount = 0.0

        for line_no in range(1, line_count + 1):
            product = random.choice(products)
            amount = round(random.uniform(250, 150000), 2)
            if random.random() < 0.08:
                amount *= -1
            total_amount += amount
            invoice_lines.append(
                {
                    "invoice_id": invoice_id,
                    "line_no": line_no,
                    "product_id": product["product_id"],
                    "account": random.choice(ACCOUNTS),
                    "tax_code": random.choice(TAX_CODES),
                    "quantity": random.randint(1, 50),
                    "amount": round(amount, 2),
                    "currency": currency,
                    "source_reference": f"SYN-{idx:06d}-{line_no:02d}",
                }
            )

        invoices.append(
            {
                "invoice_id": invoice_id,
                "entity_id": entity.entity_id,
                "counterparty_id": counterparty["counterparty_id"],
                "invoice_date": invoice_date.isoformat(),
                "period": invoice_date.strftime("%Y-%m"),
                "currency": currency,
                "total_amount": round(total_amount, 2),
                "source_system": random.choice(["ERP_A", "ERP_B", "ERP_C"]),
            }
        )

    return invoices, invoice_lines


def generate(output_dir: Path, seed: int, transaction_count: int) -> None:
    random.seed(seed)
    entities = make_entities()
    counterparties = make_counterparties(entities)
    products = make_products()
    invoices, invoice_lines = make_transactions(entities, counterparties, products, transaction_count)

    write_csv(output_dir / "entities.csv", [entity.__dict__ for entity in entities])
    write_csv(output_dir / "counterparties.csv", counterparties)
    write_csv(output_dir / "products.csv", products)
    write_csv(output_dir / "fx_rates.csv", make_fx_rates())
    write_csv(output_dir / "invoices.csv", invoices)
    write_csv(output_dir / "invoice_lines.csv", invoice_lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic ERP-style tax and finance data.")
    parser.add_argument("--output-dir", default="data/synthetic_erp", help="Output folder for generated CSV files.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible data.")
    parser.add_argument("--transactions", type=int, default=250, help="Number of synthetic invoices.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate(Path(args.output_dir), args.seed, args.transactions)


if __name__ == "__main__":
    main()

