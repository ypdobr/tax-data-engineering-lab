"""Synthetic SAP-style intercompany line items. Deterministic, with seeded defects."""
import random
import pandas as pd

ENTITIES = {
    "E100": {"name": "Alpha GmbH", "country": "DE", "currency": "EUR"},
    "E200": {"name": "Alpha Suisse AG", "country": "CH", "currency": "CHF"},
    "E300": {"name": "Alpha Polska Sp. z o.o.", "country": "PL", "currency": "PLN"},
    "E400": {"name": "Alpha US Inc.", "country": "US", "currency": "USD"},
}

FX_TO_EUR = {"EUR": 1.0, "CHF": 1.04, "PLN": 0.23, "USD": 0.92}

SELLER_ACCOUNTS = ["440000", "441000", "442000"]   # IC revenue
BUYER_ACCOUNTS = ["640000", "641000", "642000"]    # IC expense


def generate(n_docs: int = 400, seed: int = 26) -> pd.DataFrame:
    """Two legs per IC document (seller +, buyer -), plus five seeded defects."""
    rng = random.Random(seed)
    codes = list(ENTITIES)
    rows = []

    def leg(doc, date, company, counterparty, account, amount, currency):
        rows.append({
            "doc_id": doc, "posting_date": date, "company": company,
            "counterparty": counterparty, "account": account,
            "amount": round(amount, 2), "currency": currency,
        })

    for i in range(1, n_docs + 1):
        seller, buyer = rng.sample(codes, 2)
        doc = f"IC{i:06d}"
        date = f"2026-{rng.randint(1, 6):02d}-{rng.randint(1, 28):02d}"
        currency = ENTITIES[seller]["currency"]
        amount = rng.uniform(500, 250000)
        acc_ix = rng.randrange(3)
        leg(doc, date, seller, buyer, SELLER_ACCOUNTS[acc_ix], amount, currency)
        leg(doc, date, buyer, seller, BUYER_ACCOUNTS[acc_ix], -amount, currency)

    # Seeded defects, one per rule the validator must catch.
    leg("IC900001", "2026-03-15", "E100", "E200", "440000", 12000.00, "EUR")            # missing buyer leg
    leg("IC900002", "2026-03-16", "E100", "E300", "440000", 8000.00, "EUR")             # amount mismatch
    leg("IC900002", "2026-03-16", "E300", "E100", "640000", -7900.00, "EUR")
    leg("IC900003", "2026-03-17", "E200", "E400", "441000", 5000.00, "CHF")             # currency mismatch
    leg("IC900003", "2026-03-17", "E400", "E200", "641000", -5000.00, "USD")
    leg("IC900004", "2026-03-18", "E999", "E100", "440000", 3000.00, "EUR")             # unknown entity
    leg("IC900004", "2026-03-18", "E100", "E999", "640000", -3000.00, "EUR")
    leg("IC900005", "2026-03-19", "E300", "E100", "442000", 4400.00, "PLN")             # duplicate seller leg
    leg("IC900005", "2026-03-19", "E300", "E100", "442000", 4400.00, "PLN")
    leg("IC900005", "2026-03-19", "E100", "E300", "642000", -4400.00, "PLN")

    return pd.DataFrame(rows)


if __name__ == "__main__":
    generate().to_csv("data/synthetic_sap_lineitems.csv", index=False)
    print("wrote data/synthetic_sap_lineitems.csv")

