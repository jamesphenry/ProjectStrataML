# TFC-0003: Standard Run Execution Contract (`tools/run.py`)

**Status:** Draft
**Author:** James Henry (james.phenry@gmail.com)
**Created:** 2025-12-23

---

## 1. Summary

This document defines the **standard execution contract** for running experiments in repositories that adopt TFC-0001 and TFC-0002. It specifies how training or evaluation code is invoked, how runs are created on disk, and how metadata, metrics, and artifacts are recorded.

The goal is to provide a **minimal, MLflow-lite execution model** implemented locally via a reference tool (`tools/run.py`), without requiring any external services.

---

## 2. Motivation

Even with a standardized repository layout and schemas, ML projects often diverge in how runs are launched and recorded. This leads to:

* Inconsistent run directory creation
* Missing or incomplete metadata
* Non-reproducible executions

A standard run execution contract ensures that:

* Every run is recorded consistently
* Tooling can reason about runs mechanically
* Humans can trust the contents of `runs/`

---

## 3. Goals

* Define a canonical process for executing runs
* Specify required side effects on the repository
* Keep the execution model framework-agnostic
* Allow simple, script-based invocation

---

## 4. Non-Goals

* Implementing a scheduler or orchestrator
* Managing distributed execution
* Replacing user training code

---

## 5. Run Lifecycle Overview

A run proceeds through the following phases:

1. Invocation
2. Run directory creation
3. Metadata capture
4. User code execution
5. Metrics and artifact logging
6. Finalization

Each phase has defined inputs and outputs.

---

## 6. Invocation Contract

Runs are initiated via a standard entry point:

```
python tools/run.py --experiment experiments/exp-001.yaml
```

### Required Arguments

* `--experiment`: Path to an experiment definition file

### Optional Arguments

* `--run-id`: Explicit run identifier
* `--dry-run`: Validate configuration without execution
* `--notes`: Free-form annotation

---

## 7. Run ID Generation

If not explicitly provided, the run ID MUST be generated using the following format:

```
run-YYYY-MM-DD-XXX
```

Where `XXX` is a zero-padded, monotonically increasing index for that date.

Run IDs MUST be unique within the repository.

---

## 8. Run Directory Creation

Upon invocation, the tool MUST:

* Create a new directory under `runs/`
* Fail if the directory already exists
* Treat the directory as immutable after creation

Structure:

```
runs/run-YYYY-MM-DD-XXX/
```

---

## 9. Metadata Capture

Before user code execution, the tool MUST generate:

### 9.1 `config.yaml`

* Materialized configuration after resolving all references
* Conforms to TFC-0002 `config.yaml` schema

### 9.2 `system.json`

* OS information
* Python version
* Installed ML frameworks
* Hardware summary (best-effort)

---

## 10. User Code Execution

User code is executed after metadata capture.

Requirements:

* Training scripts MUST accept a configuration path
* Working directory SHOULD be the repository root
* Environment variables MAY be injected

Failures:

* If execution fails, the run directory MUST remain
* Failure state SHOULD be logged to `logs.txt`

---

## 11. Metrics Logging Contract

Metrics MUST be written to `metrics.json`.

Rules:

* File may be updated incrementally
* Final state MUST be valid JSON
* Structure MUST conform to TFC-0002

Tools MAY provide helper functions for logging.

---

## 12. Artifact Logging Contract

Artifacts:

* MUST be stored under `runs/<run-id>/artifacts/`
* SHOULD be organized into subdirectories
* MUST NOT be modified after creation

Large artifacts MUST be tracked via Git LFS.

---

## 13. Logging

All stdout and stderr output SHOULD be captured into:

```
runs/<run-id>/logs.txt
```

Additional structured logs MAY be added later.

---

## 14. Finalization

On successful completion:

* `metrics.json` MUST contain final summary values
* Model artifacts MAY be copied to `models/`
* Run status SHOULD be recorded in `config.yaml`

On failure:

* Partial outputs MUST be preserved
* Failure reason SHOULD be visible in logs

---

## 15. Validation Expectations

A conforming run MUST:

* Have a valid run ID
* Contain `config.yaml`
* Conform to TFC-0002 schemas

Validation tooling MAY refuse to index invalid runs.

---

## 16. Future Compatibility

This execution contract is intentionally compatible with:

* MLflow run semantics
* W&B offline logging
* Future centralized runners or dashboards

---

## 17. Open Questions

* Standard environment variable names
* Support for multi-process runs
* Optional run status file

---

## 18. Appendix

This TFC completes the **minimum viable local ML framework** when combined with:

* TFC-0001 (Repository Layout)
* TFC-0002 (Schemas)

No external services are required.

