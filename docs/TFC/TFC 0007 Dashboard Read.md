# TFC-0007: Dashboard Read API and Workspace Indexing

**Status:** Draft
**Author:** James Henry (james.phenry@gmail.com)
**Created:** 2025-12-23

---

## 1. Summary

This document defines a **read-only dashboard API contract** for repositories compliant with TFC-0001 through TFC-0006. It specifies how tools may **index, query, and visualize** repository contents (datasets, runs, models, and lineage) without mutating state.

The API is designed to support:

* Local dashboards
* CLI explorers
* Static site generation
* Future remote or federated viewers

---

## 2. Motivation

Once repositories are structured and validated, they become valuable sources of truth. However, without a standard read interface, each dashboard or tool must reimplement discovery logic.

This TFC establishes:

* A canonical indexing model
* Stable query semantics
* A separation between **artifact truth (filesystem)** and **presentation (dashboard)**

---

## 3. Goals

* Define a read-only contract
* Avoid requiring a running service
* Enable fast indexing and caching
* Support multiple frontends over the same data

---

## 4. Non-Goals

* Mutating repository state
* Authentication or authorization
* Replacing Git history

---

## 5. Conceptual Model

A compliant repository exposes a **workspace** composed of:

* Datasets
* Runs
* Models
* Derived lineage edges

Dashboards operate by building a **workspace index**.

---

## 6. Workspace Index

The workspace index is a logical, in-memory representation built by scanning the repository.

### Required Entities

* `Dataset`
* `Run`
* `Model`

### Required Relationships

* Dataset → Run
* Run → Model
* Dataset → Dataset (derivation)

---

## 7. Index Build Process

Indexing MUST:

1. Validate repository with TFC-0006 doctor
2. Scan canonical directories
3. Parse metadata files
4. Resolve lineage references
5. Emit a normalized index

Indexing MUST NOT:

* Modify files
* Execute training code

---

## 8. Canonical Query Interface

The following logical queries MUST be supported by any dashboard implementation:

### List Queries

* List datasets
* List runs
* List models

### Detail Queries

* Dataset by name/version
* Run by ID
* Model by name/version

### Relationship Queries

* Runs for dataset
* Models for run
* Models for dataset

---

## 9. Optional Query Extensions

Implementations MAY support:

* Filtering by metric thresholds
* Time-based queries
* State-based model queries (e.g., production models)

---

## 10. API Shapes (Logical)

This TFC defines **logical API shapes**, not transport.

Example (conceptual):

```
GET workspace.datasets
GET workspace.runs
GET workspace.models
GET dataset/{name}/{version}
GET run/{id}
GET model/{name}/{version}
```

Implementations MAY use:

* Python APIs
* REST
* GraphQL
* Static JSON exports

---

## 11. Caching and Performance

* Indexes SHOULD be cached
* Incremental rebuilds are encouraged
* Hash-based invalidation MAY be used

---

## 12. Visualization Guidance (Non-Normative)

Dashboards commonly include:

* Dataset browsers
* Run timelines
* Metric plots
* Model comparison tables
* Lineage graphs

This TFC does not mandate UI.

---

## 13. Compatibility Mapping

This API maps naturally to:

* MLflow tracking views
* TensorBoard experiment views
* Weights & Biases dashboards
* Hugging Face Spaces (read-only)

---

## 14. Validation

Dashboards SHOULD refuse to load repositories that fail TFC-0006 validation.

---

## 15. Future Extensions

Possible future TFCs may define:

* Write APIs
* Multi-repo aggregation
* Remote indexing protocols

---

## 16. Appendix

This TFC enables **human interaction** with the framework defined by:

* TFC-0001 through TFC-0006

It is intentionally conservative and read-only.

