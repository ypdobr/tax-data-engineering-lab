# Databricks Mapping

This lab uses local Python and CSV files, but the architecture maps directly to common Databricks Data Engineer Associate exam topics.

## Medallion Mapping

| Layer | Local lab artifact | Databricks concept |
| --- | --- | --- |
| Bronze | `data/pipeline_run/bronze_synthetic_erp/*.csv` | raw source tables from batch ingestion |
| Silver | `data/pipeline_run/silver_processed/canonical_transactions.csv` | cleaned and standardized transaction table |
| Silver quality | `data/pipeline_run/silver_processed/validation_exceptions.csv` | data quality checks and exception handling |
| Gold | `data/pipeline_run/gold_reporting/intercompany_transaction_review.csv` | reporting table for review and analytics |
| Monitoring | `data/pipeline_run/monitoring/run_manifest.csv` | job run metadata, row counts and reconciliation |

## Exam Domain Coverage

### Databricks Intelligence Platform

The local repo represents the same separation Databricks expects in production: source data, transformation code, scheduled jobs, governance notes and review outputs.

### Data Ingestion and Loading

The synthetic ERP generator creates repeatable batch inputs. In Databricks, this would become source files in cloud storage or a volume, with ingestion into bronze tables.

### Data Transformation and Modeling

The canonical model converts raw invoice, line, entity, counterparty, product and foreign-exchange tables into one transaction model. The validation queue captures missing rates, duplicate references, invalid tax codes, domestic group transactions and negative amounts.

### Lakeflow Jobs

`tax_data_lab.run_pipeline` represents a job graph:

1. Generate or ingest source data.
2. Build canonical transactions.
3. Write validation exceptions.
4. Build reporting shape.
5. Write monitoring manifest.

In Databricks this would become a Lakeflow job with task dependencies and retries.

### CI/CD

The repo is Git-based. The next step is to add automated checks around row counts, validation rules and output schema stability.

### Troubleshooting, Monitoring and Optimization

The run manifest gives the basic monitoring signals:

- requested invoice count
- raw invoice rows
- raw invoice-line rows
- canonical transaction rows
- validation exception rows
- reporting output rows

These counts are enough to discuss failed ingestion, transformation drift, unexpected exception spikes and downstream report changes.

### Governance and Security

The lab uses synthetic data only. A Databricks implementation would add Unity Catalog objects, table ownership, access control, lineage and separation between development and production workspaces.

## Local Practice Command

```bash
python -m tax_data_lab.run_pipeline --base-dir data/pipeline_run --transactions 500 --seed 42
```

Expected outputs:

- `data/pipeline_run/bronze_synthetic_erp`
- `data/pipeline_run/silver_processed`
- `data/pipeline_run/gold_reporting`
- `data/pipeline_run/monitoring/run_manifest.csv`
