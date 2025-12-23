# ProjectStrataML

*From datasets to models: a full lifecycle, offline-first ML framework.*

This repository defines a **self-contained, reproducible ML framework** based on a set of **Technical Framework Contracts (TFCs)**. It provides standards for repository layout, datasets, runs, models, validation, and optional artifact signing, enabling consistent project management without requiring centralized infrastructure.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Repository Layout](#repository-layout)
3. [Datasets](#datasets)
4. [Runs](#runs)
5. [Models](#models)
6. [Validation](#validation)
7. [Dashboard & Indexing](#dashboard--indexing)
8. [Artifact Signing & Checksums](#artifact-signing--checksums)
9. [Getting Started](#getting-started)
10. [Future Extensions](#future-extensions)

---

## 1. Introduction

ProjectStrataML enables you to manage **datasets, models, and runs** in a Git-native, offline-first way. All artifacts are versioned, auditable, and optionally signed. The framework is designed to work with local tools, dashboards, and CI pipelines.

It is **fork-and-forget**: no external servers or infrastructure are required.

---

## 2. Repository Layout

The repository conforms to **TFC-0001**:

```
repo-root/
├── datasets/
├── runs/
├── models/
├── tools/
├── experiments/
└── tfc/  # All TFC documents
```

* All large artifacts are tracked via **Git LFS**.
* `tools/` contains scripts for execution and validation.

---

## 3. Datasets

Defined in **TFC-0004**:

* Versioned directories: `datasets/<name>/v1/`
* Each version contains `metadata.yaml` describing provenance, splits, and content hash
* Immutable and Git LFS tracked

Usage example:

```
datasets/cifar10/v1/
  ├── train/
  ├── val/
  ├── test/
  └── metadata.yaml
```

---

## 4. Runs

Defined in **TFC-0002 & TFC-0003**:

* Runs are created via `tools/run.py`
* Stored in `runs/run-YYYY-MM-DD-XXX/`
* Include `config.yaml`, `metrics.json`, `system.json`, and `logs.txt`
* Metrics and artifacts are versioned and tracked

Run example:

```
python tools/run.py --experiment experiments/my_experiment.yaml
```

---

## 5. Models

Defined in **TFC-0005**:

* Stored under `models/<model-name>/v1/`
* Include model artifact, `metadata.yaml`, `metrics.yaml`, and `card.md`
* Versioned and immutable
* Optional promotion states: experimental, staging, production, archived

Example:

```
models/resnet50/v1/
  ├── model.pt
  ├── metadata.yaml
  ├── metrics.yaml
  └── card.md
```

---

## 6. Validation

Defined in **TFC-0006**:

* `tools/doctor.py` validates repository structure, datasets, runs, and models
* Distinguishes errors and warnings
* Can be integrated into CI pipelines

Run validation:

```
python tools/doctor.py --strict
```

---

## 7. Dashboard & Indexing

Defined in **TFC-0007**:

* Workspace indexing provides read-only access to datasets, runs, and models
* Supports dashboards, CLI explorers, or static site generation
* No repository mutation is required

---

## 8. Artifact Signing & Checksums

Defined in **TFC-0008** (optional but recommended):

* `CHECKSUMS.txt` and `SIGNATURE.asc` files verify artifact integrity
* Supports reproducibility and secure sharing
* Verification can be automated via `doctor.py`

---

## 9. Getting Started

1. Clone the repository
2. Install Git LFS and pull large files
3. Validate repository:

   ```
   python tools/doctor.py --strict
   ```
4. Run an experiment:

   ```
   python tools/run.py --experiment experiments/my_experiment.yaml
   ```
5. Explore workspace via dashboard or index scripts
6. Add new datasets or models following TFCs

---

## 10. Future Extensions

* Remote or federated dashboard views
* Multi-repository aggregation
* Enhanced artifact signing with multiple signers
* Automated metric aggregation

---

ProjectStrataML provides **offline-first, reproducible ML workflows** with a strong emphasis on **auditability, lineage, and integrity**.
