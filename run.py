"""End to end: generate -> validate -> quarantine -> matrix -> files."""
from pathlib import Path

from src.generate import generate
from src.matrix import build_matrix
from src.validate import split_clean, validate


def main() -> None:
    Path("data").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)

    df = generate()
    df.to_csv("data/synthetic_sap_lineitems.csv", index=False)

    exceptions = validate(df)
    clean, quarantined = split_clean(df, exceptions)
    matrix = build_matrix(clean)

    exceptions.to_csv("output/exceptions.csv", index=False)
    matrix.to_excel("output/ic_matrix.xlsx")

    print(f"line items      : {len(df)}")
    print(f"documents       : {df['doc_id'].nunique()}")
    print(f"exceptions      : {len(exceptions)} docs -> output/exceptions.csv")
    print(f"quarantined legs: {len(quarantined)}")
    print(f"matrix          : output/ic_matrix.xlsx")
    print()
    print(matrix.to_string())


if __name__ == "__main__":
    main()

