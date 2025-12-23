# TFC-0008: Artifact Signing and Checksums

**Status:** Draft
**Author:** James Henry (james.phenry@gmail.com)
**Created:** 2025-12-23

---

## 1. Summary

This document defines the **artifact signing and checksum contract** for ML projects following TFC-0001 through TFC-0007. Its purpose is to provide **data integrity, authenticity, and reproducibility** guarantees for datasets, models, and run artifacts.

Artifact signing and checksums are optional but highly recommended for high-integrity workflows.

---

## 2. Motivation

Repositories can contain large and critical artifacts. Common risks include:

* Accidental corruption
* Silent data drift
* Unauthorized modifications
* Reproducibility failures

By standardizing signing and checksum rules, all stakeholders can verify artifact integrity and authenticity independently.

---

## 3. Goals

* Provide clear checksum and signing standards
* Cover datasets, models, and run artifacts
* Ensure reproducible verification
* Support offline validation

---

## 4. Non-Goals

* Encrypting artifacts
* Handling secrets or credentials
* Replacing Git integrity checks (Git still required)

---

## 5. Checksum Contract

### 5.1 Supported Algorithms

* `sha256` (preferred)
* `sha512` (optional)

### 5.2 Checksum Storage

* Every artifact version directory MUST contain a file: `CHECKSUMS.txt`
* Format:

```
<algorithm> <hash> <relative-path>
```

### 5.3 Example

```
sha256 e3b0c44298fc1c149afbf4c8996fb924 datasets/cifar10/v1/train/data.bin
sha256 5d41402abc4b2a76b9719d911017c592 models/resnet50/v1/model.pt
```

---

## 6. Signing Contract

### 6.1 Signature Purpose

* Guarantees that an artifact directory has not been tampered with
* Confirms the identity of the creator or maintainer

### 6.2 Supported Signing Methods

* OpenPGP / GPG signatures (ASCII-armored)
* Detached signature files: `SIGNATURE.asc`

### 6.3 Signature Storage

* Stored alongside artifact directory (same level)
* Example:

```
datasets/cifar10/v1/SIGNATURE.asc
models/resnet50/v1/SIGNATURE.asc
```

### 6.4 Verification Contract

A compliant verification tool MUST:

* Verify all checksums match declared values
* Verify signature is valid for a trusted key
* Emit errors on mismatch or untrusted signatures

---

## 7. Workflow Recommendations

### Signing Artifacts

1. Compute checksums for all files
2. Generate `CHECKSUMS.txt`
3. Sign the directory or `CHECKSUMS.txt`
4. Commit to Git (metadata only, use Git LFS for binaries)

### Verification

* Verify before use in runs, dashboards, or exports
* CI may enforce verification as part of pipeline

---

## 8. Integration with TFCs

* **Datasets:** TFC-0004 checksum + optional signature
* **Runs:** TFC-0002 metrics and artifact checksum verification
* **Models:** TFC-0005 model artifacts signed + checksums
* **Doctor Tool (TFC-0006):** SHOULD optionally verify signatures and checksums

---

## 9. Optional Fields in Metadata

* `checksum_algorithm` (string)
* `checksum_value` (string)
* `signature_method` (string)
* `signed_by` (string, key identifier)
* `signature_verified` (boolean)

---

## 10. Future Compatibility

Artifact signing and checksums enable:

* Trustless sharing of datasets and models
* CI/CD pipeline enforcement
* Optional integration with external registries

---

## 11. Open Questions

* Handling partial or incremental artifacts
* Standardizing key distribution
* Support for multiple signers

---

## 12. Appendix

This TFC is **additive**, not mandatory, and works alongside:

* TFC-0001 through TFC-0007
* Repository Doctor validation
* Workspace indexing

Adopting this TFC enhances security and reproducibility guarantees.

