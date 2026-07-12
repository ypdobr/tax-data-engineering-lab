import pandas as pd
import pytest

from src.generate import ENTITIES, FX_TO_EUR, generate
from src.matrix import build_matrix
from src.validate import split_clean, validate


@pytest.fixture(scope="module")
def df():
    return generate()


@pytest.fixture(scope="module")
def exceptions(df):
    return validate(df)


def test_every_seeded_defect_is_caught(exceptions):
    got = dict(zip(exceptions["doc_id"], exceptions["rule"]))
    assert got["IC900001"] == "R1_MISSING_COUNTERLEG"
    assert got["IC900002"] == "R2_AMOUNT_MISMATCH"
    assert got["IC900003"] == "R3_CURRENCY_MISMATCH"
    assert got["IC900004"] == "R4_UNKNOWN_ENTITY"
    assert got["IC900005"] == "R5_DUPLICATE_LEG"


def test_no_false_positives(exceptions):
    assert len(exceptions) == 5  # exactly the seeded defects, nothing else


def test_clean_docs_net_to_zero(df, exceptions):
    clean, _ = split_clean(df, exceptions)
    net = clean.groupby("doc_id")["amount"].sum().abs().max()
    assert net <= 0.005


def test_matrix_diagonal_is_zero(df, exceptions):
    clean, _ = split_clean(df, exceptions)
    m = build_matrix(clean)
    for c in ENTITIES:
        assert m.loc[c, c] == 0.0


def test_matrix_total_equals_clean_seller_legs(df, exceptions):
    clean, _ = split_clean(df, exceptions)
    m = build_matrix(clean)
    sellers = clean[clean["amount"] > 0]
    expected = round(sum(round(r.amount * FX_TO_EUR[r.currency], 2) for r in sellers.itertuples()), 2)
    assert round(m.loc["TOTAL_PURCHASES", "TOTAL_SALES"], 2) == expected

