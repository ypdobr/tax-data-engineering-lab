# Databricks Data Engineer Associate Prep

Reference:
`C:\Users\Yurii\Documents\Codex\manager_anchor_execution\references\Databricks_Data_Engineer_Associate_Exam_Guide_May_2026.pdf`

Goal:
Use this repo as the practical training object for the exam domains while keeping the profile anchored in tax and finance data engineering.

## Exam Domains

| Domain | Weight | Lab action |
| --- | ---: | --- |
| Databricks Intelligence Platform | 6% | explain workspace, compute, notebooks, jobs and platform objects |
| Data Ingestion and Loading | 21% | create bronze-style synthetic ERP source files |
| Data Transformation and Modeling | 22% | build canonical transaction model and validation queue |
| Working with Lakeflow Jobs | 16% | use `tax_data_lab.run_pipeline` as the local job graph |
| Implementing CI/CD | 10% | keep code in Git and add schema/row-count checks |
| Troubleshooting, Monitoring and Optimization | 10% | use run manifest for row counts, exceptions and drift |
| Governance and Security | 15% | document synthetic-data boundaries, lineage and access-control mapping |

## Free Study Route

1. Use the official exam guide as the scope boundary.
2. Use Databricks Academy self-paced modules where available through a free Databricks Academy login.
3. Use Databricks Free Edition or a Community/Trial workspace only for hands-on UI practice if access is available.
4. Use this repo locally for the portfolio-grade version of the same concepts.

## Practical Exercises

### Exercise 1: Pipeline Run

```bash
python -m tax_data_lab.run_pipeline --base-dir data/pipeline_run --transactions 500 --seed 42
```

Check:

- bronze source tables exist
- silver canonical transactions exist
- validation exceptions exist
- gold intercompany review rows exist
- monitoring manifest has stable row counts

### Exercise 2: Explain the Job Graph

Write a short answer:

The pipeline has five tasks: ingestion, canonical modeling, validation, reporting shape and monitoring. Task dependencies protect output quality because each downstream step depends on a controlled upstream table.

### Exercise 3: Data Quality

Explain each validation exception:

- missing foreign-exchange rate
- invalid tax code
- duplicate source reference
- domestic group transaction
- negative amount review

### Exercise 4: Governance

Map the local files to governed Databricks assets:

- source files to bronze tables
- canonical transactions to silver table
- intercompany review to gold table
- run manifest to operational monitoring table
- schema docs to data contracts

## Mock Questions To Drill

1. Which layer should keep the raw ERP-style files before cleaning?
2. Which layer should hold the standardized transaction model?
3. Why should validation exceptions be written as data instead of only printed as logs?
4. What does a row-count manifest help troubleshoot?
5. What belongs in Unity Catalog when this becomes a managed Databricks implementation?

## LinkedIn Use After Completion

Use:
Data engineering, lakehouse pipelines, transformation logic, data quality, monitoring, governance, SQL/Python and production workflow design.

Avoid:
Generic cloud positioning or dashboard-only language.
