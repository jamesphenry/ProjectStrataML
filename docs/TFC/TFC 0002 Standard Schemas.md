# TFC-0002: Standard Schemas for Runs, Metrics, and System Metadata

**Status:** Draft
**Author:** James Henry (james.phenry@gmail.com)
**Created:** 2025-12-23

---

## 1. Summary

This document defines **standard, machine-readable schemas** for execution records within an ML project repository adopting TFC-0001. These schemas formalize how **runs, metrics, and system metadata** are recorded so that tools, scripts, and future dashboards can reliably parse and reason about experiment results.

The schemas are intentionally simple, human-readable, and framework-agnostic.

---

## 2. Motivation

Without standard schemas, ML projects suffer from:

* Inconsistent metric naming
* Unclear provenance of models
* Difficulty comparing runs
* Fragile ad-hoc parsing logic

By standardizing run-related metadata:

* Reproducibility improves
* Automation becomes feasible
* Future platform ingestion is trivial

---

## 3. Goals

* Define canonical schemas for:

  * Run configuration
  * Metrics
  * System/environment metadata
* Keep schemas JSON/YAML based
* Ensure schemas are extensible
* Avoid dependence on external services

---

## 4. Non-Goals

* Defining visualization formats
* Mandating specific metric names
* Enforcing a training framework

---

## 5. Run Directory Contract

Each run directory **MUST** follow this structure:

```
runs/
└── run-YYYY-MM-DD-XXX/
    ├── config.yaml
    ├── metrics.json
    ├── system.json
    ├── logs.txt
    └── artifacts/
```

All files are optional except `config.yaml`.

---

## 6. `config.yaml` Schema (Run Configuration)

Purpose:

* Capture the full configuration used for a run
* Enable exact reproduction

### Required Fields

```
run_id: string
experiment: string
model: string
dataset: string
```

### Recommended Fields

```
code:
  repo: string
  commit: string

training:
  epochs: int
  batch_size: int
  optimizer: string

seed: int
started_at: iso8601 timestamp
```

### Example

```
run_id: run-2025-01-10-001
experiment: exp-001-baseline
model: resnet50:v1
dataset: cifar10:v1

code:
  repo: local
  commit: a1b2c3d4

training:
  epochs: 100
  batch_size: 64
  optimizer: adam

seed: 42
started_at: 2025-01-10T14:22:00Z
```

---

## 7. `metrics.json` Schema

Purpose:

* Record quantitative outputs of a run
* Support both final values and time series

### Structure

```
{
  "summary": { string: number },
  "history": {
    string: [ { "step": number, "value": number } ]
  }
}
```

### Example

```
{
  "summary": {
    "accuracy": 0.923,
    "loss": 0.31
  },
  "history": {
    "loss": [
      {"step": 1, "value": 1.2},
      {"step": 2, "value": 0.9}
    ],
    "accuracy": [
      {"step": 1, "value": 0.62},
      {"step": 2, "value": 0.71}
    ]
  }
}
```

---

## 8. `system.json` Schema

Purpose:

* Capture execution environment details
* Support debugging and performance analysis

### Structure

```
{
  "os": string,
  "python": string,
  "frameworks": { string: string },
  "hardware": {
    "cpu": string,
    "gpus": [string],
    "ram_gb": number
  }
}
```

### Example

```
{
  "os": "Linux 6.6",
  "python": "3.11.6",
  "frameworks": {
    "torch": "2.2.0",
    "cuda": "12.1"
  },
  "hardware": {
    "cpu": "AMD EPYC 7302",
    "gpus": ["RTX 3090"],
    "ram_gb": 128
  }
}
```

---

## 9. Logs

`logs.txt` is free-form text.

Recommended content:

* Stdout/stderr
* Training progress
* Warnings and errors

No schema is enforced.

---

## 10. Artifact Guidelines

Artifacts may include:

* Images
* Audio
* Serialized tensors
* Debug outputs

Rules:

* Stored under `artifacts/`
* Tracked with Git LFS
* Immutable after creation

---

## 11. Validation Expectations

Tooling MAY validate:

* Presence of required files
* Required fields in schemas
* JSON/YAML correctness

Invalid runs SHOULD be flagged but not deleted.

---

## 12. Future Compatibility

These schemas are intentionally compatible with:

* MLflow run concepts
* W&B metrics model
* Hugging Face training metadata

---

## 13. Open Questions

* Standardized metric naming conventions
* Optional schema versioning
* Support for distributed runs

---

## 14. Appendix

This TFC builds directly on TFC-0001 and should be adopted together with it.

