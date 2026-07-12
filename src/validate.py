"""Full-population validation of IC line items. Every document, every rule, every run."""
import pandas as pd

from src.generate import ENTITIES

RULES = {
    "R1_MISSING_COUNTERLEG": "Document has only one leg",
    "R2_AMOUNT_MISMATCH": "Legs do not net to zero in transaction currency",
    "R3_CURRENCY_MISMATCH": "Legs booked in different currencies",
    "R4_UNKNOWN_ENTITY": "Company or counterparty not in entity master",
    "R5_DUPLICATE_LEG": "Same leg booked more than once",
}


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Return an exception table: doc_id, rule, detail. Clean docs never appear."""
    ex = []

    known = set(ENTITIES)
    bad_entity = df[~df["company"].isin(known) | ~df["counterparty"].isin(known)]
    for doc in sorted(bad_entity["doc_id"].unique()):
        ex.append((doc, "R4_UNKNOWN_ENTITY", RULES["R4_UNKNOWN_ENTITY"]))

    dup = df[df.duplicated(subset=["doc_id", "company", "account", "amount"], keep=False)]
    for doc in sorted(dup["doc_id"].unique()):
        ex.append((doc, "R5_DUPLICATE_LEG", RULES["R5_DUPLICATE_LEG"]))

    flagged = {d for d, _, _ in ex}
    for doc, g in df.groupby("doc_id"):
        if doc in flagged:
            continue
        if len(g) != 2:
            ex.append((doc, "R1_MISSING_COUNTERLEG", RULES["R1_MISSING_COUNTERLEG"]))
            continue
        if g["currency"].nunique() != 1:
            ex.append((doc, "R3_CURRENCY_MISMATCH", RULES["R3_CURRENCY_MISMATCH"]))
            continue
        if abs(g["amount"].sum()) > 0.005:
            ex.append((doc, "R2_AMOUNT_MISMATCH", RULES["R2_AMOUNT_MISMATCH"]))

    return pd.DataFrame(ex, columns=["doc_id", "rule", "detail"])


def split_clean(df: pd.DataFrame, exceptions: pd.DataFrame):
    """Clean line items (matrix input) vs. quarantined ones."""
    bad = set(exceptions["doc_id"])
    return df[~df["doc_id"].isin(bad)].copy(), df[df["doc_id"].isin(bad)].copy()

