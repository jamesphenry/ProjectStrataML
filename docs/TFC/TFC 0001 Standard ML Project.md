# TFC-0001: Standard ML Project Repository Layout

**Status:** Draft
**Author:** James Henry (james.phenry@gmail.com)
**Created:** 2025-12-23

---

## 1. Summary

This document defines a **standard, fork-and-forget repository layout** for machine learning projects. The goal is to provide a consistent, reproducible, and future-proof structure that supports datasets, models, experiments, and monitoring artifacts **entirely within Git**, using **Git LFS** for large files.

This layout is designed to work **without external infrastructure dependencies** (no MinIO, no LXC, no Kubernetes) while remaining compatible with future ingestion into a unified ML dashboard or platform.

---

## 2. Motivation

Machine learning projects frequently suffer from:

* Ad-hoc directory structures
* Untracked datasets and model artifacts
* Tight coupling to specific platforms or services
* Poor reproducibility

This TFC proposes a **canonical repository contract** that:

* Can be forked once and used indefinitely
* Encodes ML best practices in structure, not tooling
* Replaces early-stage needs for MLflow, W&B, or Hugging Face Hub
* Allows later migration to more advanced infrastructure without restructuring

---

## 3. Goals

* Define a **single, standard repository layout** for ML projects
* Support **Git LFS–backed datasets, models, and artifacts**
* Separate **intent (experiments)** from **results (runs)**
* Enable reproducibility via structured metadata
* Remain storage- and framework-agnostic

---

## 4. Non-Goals

* Providing a hosted service
* Mandating a specific ML framework (PyTorch, JAX, etc.)
* Replacing Git as the source of truth
* Defining runtime orchestration or infrastructure

---

## 5. Repository Root Layout

```
ml-project/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── requirements-gpu.txt
├── .gitignore
├── .gitattributes
├── .lfsconfig
├── configs/
├── data/
├── datasets/
├── models/
├── experiments/
├── runs/
├── scripts/
├── src/
├── spaces/
├── docs/
├── tools/
└── environments/
    └── system.yaml
```

This layout is **mandatory** for all projects adopting this TFC.

---

## 6. Environment Management (TFC-0010)

### 6.1 Dependency Files

Three requirements files are **mandatory**:

```
requirements.txt          # Core ML and framework dependencies
requirements-dev.txt      # Development and testing dependencies
requirements-gpu.txt       # Optional GPU-enabled dependencies
```

### 6.2 Virtual Environment

All development **MUST** use Python virtual environments:

* Recommended directory: `.venv/`
* Minimum Python version: 3.11+
* Required packages specified in requirements files

### 6.3 System Requirements

Linux-only support with detailed system requirements documented in:
`environments/system.yaml`

---

## 7. Git LFS Configuration

### 6.1 `.gitattributes`

```
# Datasets
data/** filter=lfs diff=lfs merge=lfs -text
datasets/** filter=lfs diff=lfs merge=lfs -text

# Models
models/**/*.pt filter=lfs diff=lfs merge=lfs -text
models/**/*.ckpt filter=lfs diff=lfs merge=lfs -text
models/**/*.onnx filter=lfs diff=lfs merge=lfs -text

# Run artifacts
runs/**/artifacts/** filter=lfs diff=lfs merge=lfs -text
```

### 6.2 `.lfsconfig`

```
[lfs]
fetchrecentrefsdays = 7
pruneoffsetdays = 3
```

---

## 7. Directory Specifications

### 7.1 `configs/` – Declarative Configuration

Purpose:

* Centralize all hyperparameters and runtime configuration
* Eliminate hard-coded values in code

Structure:

```
configs/
├── base.yaml
├── datasets/
├── models/
├── training/
└── sweeps/
```

Example:

```
epochs: 100
batch_size: 64
learning_rate: 3e-4
```

---

### 7.2 `data/` – Raw Inputs (Immutable)

Purpose:

* Store raw, external, or intermediate data

Rules:

* Git LFS only
* Never modified in-place
* Append-only

Structure:

```
data/
├── raw/
├── external/
└── interim/
```

---

### 7.3 `datasets/` – Versioned Datasets

Purpose:

* Represent curated, structured datasets
* Track dataset lineage and versions

Structure:

```
datasets/
├── dataset-name/
│   ├── v1/
│   │   ├── train/
│   │   ├── val/
│   │   ├── test/
│   │   └── metadata.yaml
│   └── v2/
└── README.md
```

Example `metadata.yaml`:

```
name: cifar10
version: v1
source: torchvision
hash: sha256:...
created_at: 2025-01-10
```

---

### 7.4 `models/` – Model Registry

Purpose:

* Store trained model artifacts
* Track evaluation metrics and provenance

Structure:

```
models/
├── model-name/
│   ├── v1/
│   │   ├── model.pt
│   │   ├── metrics.yaml
│   │   └── card.md
│   └── v2/
└── README.md
```

---

### 7.5 `experiments/` – Experiment Intent

Purpose:

* Describe planned experiments
* Capture design intent separately from results

Structure:

```
experiments/
├── exp-001.yaml
├── exp-002.yaml
└── README.md
```

---

### 7.6 `runs/` – Execution Records

Purpose:

* Capture immutable execution outputs
* Replace early-stage MLflow/W&B functionality

Structure:

```
runs/
├── run-YYYY-MM-DD-XXX/
│   ├── config.yaml
│   ├── logs.txt
│   ├── metrics.json
│   ├── system.json
│   └── artifacts/
```

Rules:

* Write-once
* Never modified
* Artifacts tracked via Git LFS

---

### 7.7 `src/` – Source Code

Purpose:

* All importable, testable code

Structure:

```
src/
├── datasets/
├── models/
├── training/
├── evaluation/
└── utils/
```

---

### 7.8 `spaces/` – Interactive Apps

Purpose:

* Local equivalents of Hugging Face Spaces

Structure:

```
spaces/
├── dataset_explorer/
├── inference_demo/
└── README.md
```

---

### 7.9 `tools/` – Project Tooling

Purpose:

* CLI tools and utilities
* Proto-SDK for the repository

Structure:

```
tools/
├── run.py
├── dataset_validate.py
├── export_model.py
└── doctor.py
```

---

## 8. Fork-and-Forget Workflow

1. Fork the template repository
2. Rename the project
3. Enable Git LFS
4. Commit datasets, models, and runs
5. Do not modify the base layout

---

## 9. Future Compatibility

This layout is designed to be ingestible by future systems:

* Unified dashboards
* Model registries
* Dataset browsers
* Monitoring backends

No structural migration should be required.

---

## 10. Open Questions

* Naming conventions for run IDs
* Standard schemas for metrics
* Optional CI validation

---

## 11. Appendix

This TFC intentionally mirrors concepts from:

* Hugging Face Hub
* MLflow
* Weights & Biases

While remaining fully self-contained and infrastructure-free.


