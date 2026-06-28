# System Blueprint

## Working Name

Tax Data Engineering Lab

## Architecture Layers

1. Source layer
   - synthetic ERP-style transactional tables
   - master data tables
   - regulatory input tables

2. Canonical model
   - standardized transaction schema
   - entity, counterparty and product dimensions
   - rule metadata

3. Validation layer
   - completeness checks
   - reconciliation checks
   - classification checks
   - threshold and exception rules

4. Reporting-shape layer
   - intercompany transaction review shape
   - VAT and Intrastat check shape
   - CBAM-style input and XML-preparation shape

5. Review layer
   - exception queue
   - reviewer notes
   - evidence links
   - versioned outputs

6. AI-assisted layer
   - retrieval over self-written project documentation
   - prompt templates for review support
   - answer trace back to source text
   - human review before output acceptance

## Design Principle

Build the system around generic shapes:

- input
- normalize
- validate
- classify
- review
- document
- hand over

Specific tax use cases become configurations on top of the same data and control pattern.

## Open Design Questions

- Which local database should be used first: DuckDB or SQLite?
- Which first implementation language: Python only or Python plus SQL models?
- Should the first UI be notebook-based, Streamlit, Gradio or static documentation?
- Which module should become the first public demo?

