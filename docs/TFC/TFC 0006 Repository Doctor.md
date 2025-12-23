# TFC-0006: Repository Doctor and Validation Rules

**Status:** Draft
**Author:** James Henry (james.phenry@gmail.com)
**Created:** 2025-12-23

---

## 1. Summary

This document defines the **repository validation contract** for ML projects adopting TFC-0001 through TFC-0005. It specifies the responsibilities, checks, and failure modes of a standard validation tool (referred to as the **Repository Doctor**, typically implemented as `tools/doctor.py`).

The goal is to make the framework **self-enforcing**: a repository that passes the doctor is considered structurally and semantically valid.

---

## 2. Motivation

Even the best specifications degrade without enforcement. Common failure modes include:

* Drift from the standard layout
* Missing or malformed metadata
* Large files not tracked via Git LFS
* Broken lineage between datasets, runs, and models

A repository doctor provides:

* Early error detection
* Confidence in reproducibility
* A single source of truth for correctness
* CI-friendly validation

---

## 3. Goals

* Define a canonical set of validation checks
* Distinguish between errors and warnings
* Enable automated and human-invoked validation
* Remain fast, deterministic, and offline-capable

---

## 4. Non-Goals

* Automatically fixing issues
* Enforcing coding style or linting source code
* Validating model quality or performance

---

## 5. Invocation Contract

The doctor MUST be invocable from the repository root:

```
python tools/doctor.py
```

Optional flags:

* `--strict`: Treat warnings as errors
* `--json`: Emit machine-readable output
* `--path <dir>`: Validate a subpath only

---

## 6. Exit Codes

The doctor MUST use the following exit codes:

* `0`: No errors
* `1`: Warnings only
* `2`: One or more errors

In `--strict` mode, warnings MUST result in exit code `2`.

---

## 7. Validation Categories

Validation checks are grouped into categories. Each check MUST be classified as either an **error** or a **warning**.

---

## 8. Repository Layout Validation

**Errors**:

* Missing required top-level directories defined in TFC-0001
* Unexpected files at repository root that shadow required paths

**Warnings**:

* Empty but required directories

---

## 9. Git LFS Validation

**Errors**:

* Large files in `data/`, `datasets/`, `models/`, or `runs/` not tracked by Git LFS
* Missing `.gitattributes` or `.lfsconfig`

**Warnings**:

* LFS patterns defined but unused

---

## 10. Dataset Validation (TFC-0004)

**Errors**:

* Dataset versions missing `metadata.yaml`
* Hash mismatch between declared and actual dataset contents
* Invalid dataset version naming

**Warnings**:

* Missing optional metadata fields
* Missing recommended splits (`train/`, `val/`, `test/`)

---

## 11. Run Validation (TFC-0002, TFC-0003)

**Errors**:

* Run directories missing `config.yaml`
* Invalid run ID format
* Invalid or unparsable `metrics.json` or `system.json`

**Warnings**:

* Missing logs
* Incomplete metrics history

---

## 12. Model Validation (TFC-0005)

**Errors**:

* Model versions missing required files
* Model metadata referencing nonexistent runs or datasets
* Model artifacts not tracked via Git LFS

**Warnings**:

* Missing model cards
* Missing secondary metrics

---

## 13. Lineage Validation

**Errors**:

* Runs referencing nonexistent datasets
* Models referencing nonexistent runs
* Derived datasets missing lineage metadata

This category ensures end-to-end traceability.

---

## 14. Reporting Format

By default, the doctor SHOULD emit human-readable output.

With `--json`, output MUST conform to the following structure:

```
{
  "status": "ok" | "warning" | "error",
  "errors": [ { "code": string, "message": string, "path": string } ],
  "warnings": [ { "code": string, "message": string, "path": string } ]
}
```

---

## 15. Performance Expectations

* Doctor runs SHOULD complete in seconds on typical repositories
* Hash validation MAY be skipped or cached when possible

---

## 16. CI Integration

The doctor SHOULD be suitable for use in CI pipelines:

```
python tools/doctor.py --strict
```

CI systems MAY gate merges on a clean result.

---

## 17. Extensibility

The doctor MAY support plugins for:

* Custom dataset checks
* Organization-specific policies
* Experimental validation rules

Plugins MUST NOT weaken core validation guarantees.

---

## 18. Future Compatibility

This validation contract enables:

* Safe automation
* Repository indexing
* Dashboard ingestion
* Migration to centralized platforms

---

## 19. Open Questions

* Standard error codes registry
* Partial validation modes
* Parallel validation strategies

---

## 20. Appendix

This TFC completes the **foundational framework specification** when combined with:

* TFC-0001 (Repository Layout)
* TFC-0002 (Schemas)
* TFC-0003 (Run Execution)
* TFC-0004 (Datasets)
* TFC-0005 (Models)

A repository that passes the doctor is considered compliant.

