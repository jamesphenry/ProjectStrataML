# TFC-0004: Dataset Metadata, Versioning, and Validation Contract

**Status:** Draft
**Author:** James Henry (james.phenry@gmail.com)
**Created:** 2025-12-23

---

## 1. Summary

This document defines the **canonical contract for datasets** in repositories adopting TFC-0001 through TFC-0003. It standardizes dataset layout, metadata schemas, versioning rules, and validation requirements so datasets remain reproducible, auditable, and future-ingestible.

Datasets are treated as **immutable, versioned artifacts** with explicit provenance and structure.

---

## 2. Motivation

Datasets are the most fragile and least-disciplined part of most ML projects. Common failures include:

* Silent data changes
* Unclear train/validation/test splits
* Missing provenance
* Irreproducible preprocessing

This TFC establishes a strict dataset contract to prevent these failures while remaining lightweight and Git-native.

---

## 3. Goals

* Define a standard on-disk dataset layout
* Specify required dataset metadata
* Enforce immutability via versioning
* Enable automated dataset validation
* Preserve compatibility with future dashboards and registries

---

## 4. Non-Goals

* Providing dataset hosting or download services
* Mandating preprocessing pipelines
* Enforcing a specific data format (CSV, Parquet, images, etc.)

---

## 5. Dataset Root Layout

All datasets MUST live under the `datasets/` directory.

```
datasets/
└── <dataset-name>/
    ├── v1/
    │   ├── train/
    │   ├── val/
    │   ├── test/
    │   └── metadata.yaml
    └── v2/
```

Rules:

* `<dataset-name>` MUST be lowercase and kebab-case
* Dataset versions MUST be immutable
* New data requires a new version directory

---

## 6. Split Semantics

### Required Splits

Each dataset version SHOULD provide:

* `train/`
* `val/`
* `test/`

If a split is omitted, it MUST be explicitly documented in `metadata.yaml`.

### Alternative Structures

For datasets where splits are not applicable:

* A single `data/` directory MAY be used
* The split strategy MUST be documented

---

## 7. `metadata.yaml` Schema

Each dataset version MUST contain a `metadata.yaml` file.

### Required Fields

```
name: string
version: string
created_at: iso8601 timestamp
description: string
```

### Provenance Fields (Required)

```
source:
  type: string        # e.g. "download", "generated", "manual"
  uri: string         # URL, path, or description
  license: string
```

### Content Integrity (Required)

```
hash:
  algorithm: sha256
  value: string
```

The hash MUST represent the contents of the dataset version directory (excluding metadata).

### Optional Fields

```
splits:
  train: float
  val: float
  test: float

schema:
  format: string
  fields: list

statistics:
  num_samples: int
  size_bytes: int

derived_from:
  dataset: string
  version: string

notes: string
```

---

## 8. Example `metadata.yaml`

```
name: cifar10
version: v1
created_at: 2025-01-10T12:00:00Z
description: CIFAR-10 image classification dataset

source:
  type: download
  uri: https://www.cs.toronto.edu/~kriz/cifar.html
  license: MIT

hash:
  algorithm: sha256
  value: e3b0c44298fc1c149afbf4c8996fb924...

splits:
  train: 0.8
  val: 0.1
  test: 0.1

statistics:
  num_samples: 60000
  size_bytes: 162000000
```

---

## 9. Versioning Rules

* Dataset versions are **append-only**
* Modifying data requires a new version
* Metadata MAY be corrected in-place ONLY if data hash remains unchanged

Recommended version format:

```
v<integer>
```

---

## 10. Validation Rules

A dataset version is considered valid if:

* Directory structure conforms to this TFC
* `metadata.yaml` exists
* Required fields are present
* Declared hash matches actual contents

Validation tooling SHOULD:

* Warn on missing optional fields
* Fail on hash mismatches

---

## 11. Git LFS Requirements

All dataset contents MUST be tracked using Git LFS.

Metadata files MUST NOT be tracked via LFS.

---

## 12. Relationship to Runs and Models

* Runs MUST reference datasets as `<dataset-name>:<version>`
* Models SHOULD record the dataset version used during training
* Derived datasets MUST declare lineage via `derived_from`

---

## 13. Future Compatibility

This dataset contract is designed to map cleanly to:

* Hugging Face Datasets
* MLflow dataset tracking
* Future dataset registries

---

## 14. Open Questions

* Standard hash exclusion rules
* Optional dataset card (`README.md`) format
* Partial dataset materialization

---

## 15. Appendix

This TFC MUST be adopted together with:

* TFC-0001 (Repository Layout)
* TFC-0002 (Schemas)
* TFC-0003 (Run Execution)

Datasets are a first-class artifact in this framework.

