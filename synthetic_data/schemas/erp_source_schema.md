# ERP Source Schema

This schema is synthetic. It describes generic ERP-style tables used for local experiments.

## Tables

### entities

| Column | Meaning |
|---|---|
| entity_id | Synthetic legal entity key |
| name | Fictional entity name |
| country | Two-letter country code |
| currency | Functional currency |

### counterparties

| Column | Meaning |
|---|---|
| counterparty_id | Synthetic counterparty key |
| counterparty_name | Fictional counterparty name |
| country | Two-letter country code |
| relationship_type | `group` or `third_party` |

### products

| Column | Meaning |
|---|---|
| product_id | Synthetic product key |
| category | Product category |
| description | Fictional product description |
| commodity_code | Synthetic commodity code |

### invoices

| Column | Meaning |
|---|---|
| invoice_id | Synthetic invoice key |
| entity_id | Reporting entity |
| counterparty_id | Counterparty |
| invoice_date | Invoice date |
| period | Reporting period |
| currency | Invoice currency |
| total_amount | Total invoice amount |
| source_system | Fictional source system |

### invoice_lines

| Column | Meaning |
|---|---|
| invoice_id | Parent invoice |
| line_no | Line number |
| product_id | Product key |
| account | Synthetic account code |
| tax_code | Synthetic tax code |
| quantity | Quantity |
| amount | Line amount |
| currency | Line currency |
| source_reference | Synthetic evidence reference |

### fx_rates

| Column | Meaning |
|---|---|
| period | Reporting period |
| currency | Currency |
| rate_to_eur | Synthetic FX rate to EUR |

