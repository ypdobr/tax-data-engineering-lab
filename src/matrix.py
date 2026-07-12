"""Build the intercompany matrix (seller x buyer, EUR) from validated line items."""
import pandas as pd

from src.generate import ENTITIES, FX_TO_EUR


def build_matrix(clean: pd.DataFrame) -> pd.DataFrame:
    """Seller rows, buyer columns, amounts in EUR. Only seller legs (amount > 0)."""
    sellers = clean[clean["amount"] > 0].copy()
    sellers["amount_eur"] = sellers.apply(
        lambda r: round(r["amount"] * FX_TO_EUR[r["currency"]], 2), axis=1
    )
    matrix = sellers.pivot_table(
        index="company", columns="counterparty", values="amount_eur",
        aggfunc="sum", fill_value=0.0,
    )
    codes = [c for c in ENTITIES if c in set(matrix.index) | set(matrix.columns)]
    matrix = matrix.reindex(index=codes, columns=codes, fill_value=0.0)
    matrix["TOTAL_SALES"] = matrix.sum(axis=1)
    matrix.loc["TOTAL_PURCHASES"] = matrix.sum(axis=0)
    return matrix.round(2)

