# Tax Data Engineering Lab

Safe public portfolio wrapper for tax, finance data engineering and applied AI.

This repository is designed as a synthetic-data lab. It must not contain client data, Deloitte materials, proprietary workflow logic, confidential templates, screenshots, extracts, or copied report structures.

## Positioning

The lab explores how tax and finance data can move from raw ERP-style tables into controlled review products:

- source ingestion
- canonical data model
- validation rules
- reporting shapes
- exception handling
- documentation
- AI-assisted review

The goal is a reusable architecture, not a clone of any client or employer workflow.

## Safe Scope

Allowed:

- synthetic ERP-style tables
- public regulatory concepts
- generic validation examples
- open-source Python code
- local RAG experiments over self-written documentation
- architecture diagrams written from first principles

Excluded:

- client names
- real transaction data
- Deloitte templates or code
- project screenshots
- copied Alteryx workflows
- copied XML/reporting packages
- proprietary mapping logic
- internal terminology that identifies a client or delivery asset

## Planned Modules

1. ERP ingestion layer
2. Canonical tax and finance data model
3. Validation rule engine
4. Reporting-shape builder
5. AI-assisted review layer
6. Documentation and handover pack

## Current Status

Wrapper created. First synthetic ERP source layer added.

## Generate Synthetic ERP Data

```bash
python -m tax_data_lab.data_generation.generate_synthetic_erp --output-dir data/synthetic_erp --transactions 250
```

The generated CSV files stay in `data/`, which is ignored by Git.

## Build Canonical Transactions

```bash
python -m tax_data_lab.canonical_model --input-dir data/synthetic_erp --output-dir data/processed
```

This writes:

- `canonical_transactions.csv`
- `validation_exceptions.csv`

## Build Reporting Shapes

```bash
python -m tax_data_lab.reporting_shapes --canonical-file data/processed/canonical_transactions.csv --output-dir data/reporting
```

This writes:

- `intercompany_transaction_review.csv`
