# Intercompany Transaction Review Shape

This output is a generic synthetic reporting shape. It is not a Deloitte template, client deliverable or copied IC Matrix structure.

## Purpose

The shape aggregates group transactions from the canonical transaction model into a reviewable entity-counterparty-period view.

It supports the portfolio story:

- raw ERP-style source tables
- canonical transaction model
- validation queue
- reviewable reporting shape

## Output

`intercompany_transaction_review.csv`

| Column | Meaning |
|---|---|
| period | Reporting period |
| entity_id | Reporting entity |
| counterparty_id | Group counterparty |
| relationship_type | Group relationship indicator |
| transaction_count | Number of transaction lines |
| gross_amount_eur | Net EUR amount |
| absolute_amount_eur | Absolute EUR transaction volume |
| tax_codes | Distinct tax codes in the group |
| commodity_codes | Distinct commodity codes in the group |
| review_flag | Generic review classification |

## Review Flags

| Flag | Meaning |
|---|---|
| standard_review | Regular review population |
| high_value | Absolute EUR amount above the synthetic threshold |
| high_volume | Transaction line count above the synthetic threshold |
| net_credit_position | Net EUR amount is negative |

## Design Boundary

This shape demonstrates aggregation, review flags and source-to-output logic. It intentionally avoids:

- client-specific columns
- real thresholds
- employer methodology
- copied report layouts
- copied mapping logic

