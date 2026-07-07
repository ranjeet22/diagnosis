# Diagnōsis - Technical Architecture Documentation

This document describes the high-level architecture design and design guidelines for Diagnōsis.

## Layers

- **Presentation Layer**: Exposes routes via FastAPI. Restricts interactions to HTTP serialization, routing, and parsing parameters.
- **Application Layer**: Houses services that orchestrate data flows. This layer has no awareness of web requests or database drivers.
- **Domain Layer**: Central schemas, enums, exceptions, and models.
- **Infrastructure Layer**: Cloud integration (GCS, BigQuery, Gemini) and local filesystem access. Swapped dynamically via Dependency Injection.

## Ingestion Architecture

Ingestion takes raw tabular datasets, runs format and encoding checks, sniffs the structure (rows, columns, headers, delimiters), and saves the dataset into localized or cloud structures under unique UUID identifiers. All downstream processes rely on this immutable identifier to query or clean the dataset.
