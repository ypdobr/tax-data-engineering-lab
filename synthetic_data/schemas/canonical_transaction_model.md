# Canonical Transaction Model

The canonical model turns synthetic source tables into one reviewable transaction table.

## Purpose

This table is the center of the lab. Reporting shapes such as intercompany review, VAT checks, Intrastat checks and CBAM-style input preparation should read from this model instead of from raw source tables.

## Output Table

`canonical_transactions.csv`

| Column | Meaning |
|---|---|
| transaction_id | Synthetic transaction-line key |
| period | Reporting period |
| entity_id | Reporting entity |
| entity_country | Reporting entity country |
| counterparty_id | Counterparty |
| counterparty_country | Counterparty country |
| relationship_type | Group or third-party indicator |
| product_id | Product key |
| product_category | Product category |
| commodity_code | Synthetic commodity code |
| account | Synthetic account code |
| tax_code | Synthetic tax code |
| amount | Source amount |
| currency | Source currency |
| fx_rate_to_eur | Synthetic FX rate |
| amount_eur | EUR converted amount |
| source_system | Fictional source system |
| source_reference | Synthetic evidence reference |

## Validation Output

`validation_exceptions.csv`

| Column | Meaning |
|---|---|
| transaction_id | Transaction requiring review |
| period | Reporting period |
| rule_id | Validation rule |
| severity | Review severity |
| source_reference | Evidence reference |

## Current Rules

- missing entity
- missing counterparty
- missing FX rate
- invalid tax code
- duplicate source reference
- domestic group transaction
- negative amount review

