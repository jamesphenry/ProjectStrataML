# TFC-0005: Model Registry, Model Cards, and Promotion Lifecycle

**Status:** Draft
**Author:** James Henry (james.phenry@gmail.com)
**Created:** 2025-12-23

---

## 1. Summary

This document defines the **model contract** for repositories adopting TFC-0001 through TFC-0004. It standardizes how trained models are stored, described, evaluated, and promoted within a repository, turning the `models/` directory into a **local-first model registry**.

Models are treated as **versioned, immutable artifacts** with explicit lineage to runs and datasets.

---

## 2. Motivation

Without a clear model contract, ML repositories often suffer from:

* Unclear “best” or “current” models
* Missing evaluation context
* Broken links between models, runs, and datasets
* Silent overwrites of trained weights

This TFC formalizes models as first-class artifacts with:

* Versioning
* Metadata
* Evaluation summaries
* Optional promotion semantics

---

## 3. Goals

* Define a canonical on-disk model layout
* Specify required and optional model metadata
* Standardize model cards
* Establish a simple promotion lifecycle
* Preserve full lineage to runs and datasets

---

## 4. Non-Goals

* Serving models
* Deploying models to production systems
* Mandating specific model formats

---

## 5. Model Root Layout

All models MUST live under the `models/` directory.

```
models/
└── <model-name>/
    ├── v1/
    │   ├── model.<ext>
    │   ├── metrics.yaml
    │   ├── card.md
    │   └── metadata.yaml
    └── v2/
```

Rules:

* `<model-name>` MUST be lowercase and kebab-case
* Model versions MUST be immutable
* Model artifacts MUST be tracked via Git LFS

---

## 6. Model Versioning

### Version Identifiers

Model versions MUST use a monotonically increasing format:

```
v<integer>
```

A new version MUST be created when:

* Training data changes
* Training code changes
* Hyperparameters change

---

## 7. `metadata.yaml` Schema (Model Metadata)

Purpose:

* Capture provenance and lineage
* Enable automation and validation

### Required Fields

```
name: string
version: string
created_at: iso8601 timestamp
run_id: string
```

### Lineage Fields (Required)

```
dataset:
  name: string
  version: string

code:
  repo: string
  commit: string
```

### Optional Fields

```
framework: string
architecture: string
parameters: int
notes: string
```

---

## 8. `metrics.yaml` Schema (Model Evaluation)

Purpose:

* Summarize model performance
* Enable comparison across versions

### Required Fields

```
primary_metric:
  name: string
  value: number
```

### Optional Fields

```
secondary_metrics:
  string: number

evaluation:
  dataset: string
  split: string

confidence_intervals:
  string:
    low: number
    high: number
```

---

## 9. Model Card (`card.md`)

Purpose:

* Human-readable documentation
* Long-term institutional memory

### Recommended Sections

* Overview
* Training Data
* Training Procedure
* Evaluation Results
* Intended Use
* Limitations
* Ethical Considerations

Model cards SHOULD be written in Markdown.

---

## 10. Promotion Lifecycle

Model versions MAY optionally participate in a promotion lifecycle.

### Standard States

* `experimental`
* `staging`
* `production`
* `archived`

### State Representation

The current state MUST be recorded in `metadata.yaml`:

```
state: production
```

Promotion MUST:

* Never modify the model artifact
* Be recorded as a metadata change only

---

## 11. Relationship to Runs

* Each model version MUST reference the originating `run_id`
* A run MAY produce zero or more models
* Promotion does not affect run records

---

## 12. Validation Rules

A model version is valid if:

* Directory structure conforms to this TFC
* Required files exist
* Metadata references a valid run and dataset
* Artifacts are tracked via Git LFS

Invalid models SHOULD be flagged by validation tooling.

---

## 13. Future Compatibility

This model contract is designed to map cleanly to:

* MLflow Model Registry
* Hugging Face Model Hub
* Future centralized registries

---

## 14. Open Questions

* Multiple evaluation datasets per model
* Automatic metric extraction from runs
* Model signing or checksum requirements

---

## 15. Appendix

This TFC completes the **artifact lifecycle** when combined with:

* TFC-0001 (Repository Layout)
* TFC-0002 (Schemas)
* TFC-0003 (Run Execution)
* TFC-0004 (Datasets)

Models are now first-class, auditable entities.

