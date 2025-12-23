# TFC-0009: Development Workflow and Versioning Schema

**Status:** Draft
**Author:** James Henry (james.phenry@gmail.com)
**Created:** 2025-12-23

---

## 1. Summary

This document defines the **standard development workflow** for ML projects adopting TFC-0001 through TFC-0008. It specifies commit message schemas, branch management strategies, release cadence aligned with model deployments, and strict validation rules to ensure reproducibility, auditability, and seamless integration with the ML artifact lifecycle.

The workflow is designed to be **Git-native**, **offline-first**, and **ML-focused** while maintaining strict compliance through automated validation.

---

## 2. Motivation

Development workflows in ML projects often suffer from:

* Inconsistent commit messages making history difficult to parse
* Complex branching strategies that don't match ML development patterns
* Release cadences disconnected from model deployment realities
* Weak integration between code changes and ML artifacts
* Lack of automated validation for development practices

This TFC establishes a **rigid yet practical** development contract that:
* Provides clear commit semantics for ML activities
* Simplifies branching to match ML workflow patterns
* Aligns releases with model deployment milestones
* Enables strict validation and auditability
* Integrates deeply with existing TFC artifact management

---

## 3. Goals

* Define ML-focused commit message types and schemas
* Establish a simple but effective branch management strategy
* Create a release cadence aligned with model deployments
* Enable strict validation through TFC-0006 doctor tool
* Ensure tight integration with existing TFC contracts
* Support offline-first development practices

---

## 4. Non-Goals

* Mandating specific CI/CD platforms
* Defining code review processes
* Replacing Git's native versioning
* Enforcing specific development tools or IDEs

---

## 5. Commit Message Schema

### 5.1 Required Format

All commits MUST follow this exact format:

```
<type>(<scope>): <description>

[optional body]

[optional metadata]
```

### 5.2 ML-Focused Types

The following commit types are MANDATORY:

* **dataset** - Dataset creation, updates, or modifications
* **model** - Model architecture changes, training code updates
* **experiment** - New experiments, experiment configuration changes
* **run** - Changes to run execution tools or scripts
* **validation** - Updates to validation rules, doctor tool changes
* **registry** - Model registry, dataset registry changes
* **tfc** - TFC document updates, framework specification changes
* **tools** - Development tools, scripts, utilities changes
* **docs** - Documentation updates not covered by TFC
* **refactor** - Code refactoring without functional changes
* **test** - Test additions, updates, or fixes
* **config** - Configuration changes not related to experiments
* **deploy** - Deployment-related changes, infrastructure updates

### 5.3 Scope Values

Scope MUST be one of:

* **core** - Core framework functionality
* **<dataset-name>** - Specific dataset being modified
* **<model-name>** - Specific model being modified  
* **<experiment-name>** - Specific experiment being modified
* **<tool-name>** - Specific tool being modified
* **<tfc-number>** - Specific TFC document being updated

### 5.4 Metadata Fields (Required for Certain Types)

For **dataset**, **model**, **experiment**, and **run** commits, the following metadata MUST be included:

```
tfc-version: affected/tfc/number
dataset-version: dataset/name:vX (for dataset commits)
model-version: model/name:vX (for model commits)
run-id: run-YYYY-MM-DD-XXX (for run commits)
experiment-file: experiments/name.yaml (for experiment commits)
breaking-change: true/false (if applicable)
```

### 5.5 Commit Examples

#### Dataset Addition
```
dataset(cifar10): add CIFAR-10 dataset v1

Imported CIFAR-10 dataset from torchvision with standard splits.
Added metadata.yaml with proper provenance and hash verification.

tfc-version: TFC-0004
dataset-version: cifar10:v1
```

#### Model Update
```
model(resnet50): update training architecture for better convergence

Modified residual blocks and learning rate schedule to improve convergence.
Updated to use AdamW optimizer with cosine annealing.

tfc-version: TFC-0005
model-version: resnet50:v2
breaking-change: true
```

#### TFC Update
```
tfc(TFC-0009): add development workflow schema

Defined ML-focused commit types, branch strategy, and release cadence.
Integrated with existing TFC contracts for strict validation.

tfc-version: TFC-0009
breaking-change: false
```

---

## 6. Branch Management Strategy

### 6.1 Core Branches

#### main (Protected)
* **Purpose:** Stable, production-ready code
* **Rules:** 
  * Direct commits are FORBIDDEN
  * MUST only accept PRs from develop or hotfix branches
  * MUST always pass all TFC-0006 validation checks
  * SHOULD be tagged for releases

#### develop (Integration)
* **Purpose:** Integration branch for feature development
* **Rules:**
  * Accepts merges from feature branches
  * MUST pass TFC-0006 validation before main merge
  * MAY be used for testing integration

### 6.2 Supporting Branches

#### feature/<name>
* **Purpose:** Feature development
* **Rules:**
  * Branch from develop
  * Naming: `feature/<feature-name>` or `feature/<tfc-number>-<description>`
  * Delete after merge to develop

#### dataset/<name>-vX
* **Purpose:** Dataset-specific work
* **Rules:**
  * Branch from develop
  * Naming: `dataset/<dataset-name>-vX`
  * Work MUST result in new dataset version

#### model/<name>-vX
* **Purpose:** Model development work
* **Rules:**
  * Branch from develop
  * Naming: `model/<model-name>-vX`
  * Work MUST result in model version update

#### hotfix/<description>
* **Purpose:** Critical fixes to production
* **Rules:**
  * Branch from main
  * MUST target both main and develop
  * Naming: `hotfix/<brief-description>`

### 6.3 Branch Protection Rules (STRICT)

The following rules MUST be enforced:

* **main branch:** No direct pushes, PR-only workflow
* **All branches:** Must pass TFC-0006 doctor validation
* **Feature branches:** Must rebase onto develop before merge
* **Dataset/Model branches:** Must result in version updates
* **Hotfix branches:** Must have validation tests passing

---

## 7. Tag and Release Contract

### 7.1 Release Cadence

Releases MUST align with **model deployments** to production:

* **Minor releases:** When models reach `production` state
* **Major releases:** Breaking changes to TFC contracts
* **Patch releases:** Critical fixes and non-breaking updates

### 7.2 Tag Format

Tags MUST follow this exact format:

```
v<major>.<minor>.<patch>-model<model-name>v<model-version>
```

Examples:
* `v1.2.0-modelresnet50v3` - Release with ResNet50 v3 to production
* `v2.0.0-tfc0009` - Major release with TFC-0009 changes
* `v1.2.1-hotfix-validation` - Patch release for validation fixes

### 7.3 Release Manifest Schema

Each release tag MUST include a `RELEASE.yaml` file:

```yaml
release:
  version: "1.2.0"
  tag: "v1.2.0-modelresnet50v3"
  created_at: "2025-12-23T14:30:00Z"
  commit_hash: "abc123def456..."
  
production_models:
  - name: "resnet50"
    version: "v3"
    run_id: "run-2025-12-20-001"
    metrics_file: "models/resnet50/v3/metrics.yaml"
    
changed_components:
  - type: "model"
    name: "resnet50"
    old_version: "v2"
    new_version: "v3"
  - type: "tfc"
    number: "TFC-0005"
    change: "Updated metadata schema"
    
validation:
  doctor_status: "passed"
  checksums_verified: true
  signatures_verified: true
  
breaking_changes:
  - "model(resnet50): architecture changes requiring retraining"
  
changelog: |
  - Promote resnet50:v3 to production with 94.2% accuracy
  - Update model registry schema per TFC-0005 v1.1
  - Fix dataset validation issues in doctor tool
```

### 7.4 Release Process

1. **Model Promotion:** Model reaches `production` state per TFC-0005
2. **Validation:** Run `tools/doctor.py --strict` validation
3. **Tag Creation:** Create tag with proper format
4. **Release Manifest:** Create `RELEASE.yaml` with all required fields
5. **Signing:** Sign release per TFC-0008 (optional but recommended)
6. **Verification:** Verify all checksums and signatures

---

## 8. Development Lifecycle Integration

### 8.1 Commit to Artifact Relationships

Every commit MUST be traceable to ML artifacts:

```yaml
# Optional .commit-meta.yaml at repo root for complex changes
commit_artifacts:
  dataset_changes:
    - dataset: "cifar10"
      versions: ["v1", "v2"]
      change_type: "add_data"
  model_changes:
    - model: "resnet50"
      versions: ["v2", "v3"]
      related_runs: ["run-2025-12-20-001", "run-2025-12-22-003"]
  experiment_changes:
    - experiment: "exp-008"
      configuration_changes: true
```

### 8.2 Run Integration

All runs MUST record the development context:

```yaml
# In runs/<run-id>/config.yaml
development_context:
  commit_hash: "abc123def456..."
  branch: "feature/resnet50-v3"
  tfc_versions:
    - "TFC-0001"
    - "TFC-0002"
    - "TFC-0009"
  development_tools:
    - name: "doctor"
      version: "1.0.0"
```

### 8.3 Model Registry Integration

Model versions MUST reference development context:

```yaml
# In models/<model>/<version>/metadata.yaml
development:
  commit_hash: "abc123def456..."
  branch_at_creation: "model/resnet50-v3"
  release_tag: "v1.2.0-modelresnet50v3"
```

---

## 9. Validation Rules (STRICT)

### 9.1 Doctor Tool Enhancements (TFC-0006 Extension)

The doctor MUST validate the following additional rules:

#### Commit Validation
* **ERROR:** Commits not following ML-focused type schema
* **ERROR:** Missing required metadata for dataset/model/experiment/run commits
* **ERROR:** Invalid scope values or naming
* **WARNING:** Missing commit metadata for other types

#### Branch Validation
* **ERROR:** Direct commits to main branch
* **ERROR:** Branches not following naming conventions
* **ERROR:** Feature branches that never merged
* **WARNING:** Long-lived feature branches (>30 days)

#### Release Validation
* **ERROR:** Release tags not following format
* **ERROR:** Missing or invalid RELEASE.yaml
* **ERROR:** Release not passing doctor validation
* **WARNING:** Unsigned releases (if signing enabled)

### 9.2 Git Hooks (Required)

The following hooks MUST be implemented:

#### pre-commit
* Validate commit message format
* Check for required metadata
* Run basic TFC-0006 checks on affected files

#### pre-push
* Run full doctor validation
* Verify branch naming conventions
* Check for missing required files

### 9.3 CI Integration Rules

CI pipelines MUST:
* Run `tools/doctor.py --strict` on every PR
* Validate commit message formats for all commits in PR
* Enforce branch protection rules
* Verify release processes

---

## 10. Tooling Integration

### 10.1 Enhanced Doctor Tool

Add the following checks to `tools/doctor.py`:

```python
# Pseudo-code for additional checks
def validate_development_workflow(repo_path):
    # Check commit message formats
    # Validate branch naming
    # Verify release manifests
    # Check git hook status
    pass

def validate_commit_history():
    # Analyze recent commits
    # Check for required metadata
    # Verify artifact traceability
    pass
```

### 10.2 Git Hooks Implementation

Example `pre-commit` hook:

```bash
#!/bin/bash
# pre-commit hook for TFC-0009 validation

commit_message=$(cat "$1")
python tools/validate_commit.py "$commit_message"
if [ $? -ne 0 ]; then
    echo "Commit message validation failed"
    exit 1
fi
```

### 10.3 Release Tool

Add `tools/release.py` for release management:

```python
# tools/release.py
def create_release(model_name, model_version):
    # Validate model exists and is in production state
    # Create release tag
    # Generate RELEASE.yaml
    # Run doctor validation
    # Optional: Sign release
    pass
```

---

## 11. Future Compatibility

This development workflow is designed to integrate with:

* **GitHub/GitLab workflows** - PR-based development
* **MLflow tracking** - Enhanced metadata integration
* **Model registry systems** - Deployment integration
* **Automated release tools** - CI/CD pipeline compatibility
* **Federated ML systems** - Multi-repository workflows

---

## 12. Open Questions

* Standard commit message length limits
* Automated changelog generation from commit history
* Integration with external model deployment systems
* Multi-model release strategies

---

## 13. Appendix

### 13.1 Commit Type Reference Matrix

| Type | Use Case | Required Metadata | Example |
|------|----------|-------------------|---------|
| dataset | Dataset changes | tfc-version, dataset-version | `dataset(cifar10): add v1` |
| model | Model changes | tfc-version, model-version | `model(resnet50): update architecture` |
| experiment | Experiment config | tfc-version, experiment-file | `experiment(exp-008): new lr schedule` |
| run | Execution tooling | tfc-version, run-id | `run(doctor): add checksum validation` |

### 13.2 Branch Naming Reference

| Branch Type | Pattern | Example | Purpose |
|-------------|---------|---------|---------|
| Feature | `feature/<name>` | `feature/resnet50-improvements` | New features |
| Dataset | `dataset/<name>-vX` | `dataset/cifar10-v2` | Dataset work |
| Model | `model/<name>-vX` | `model/resnet50-v3` | Model development |
| Hotfix | `hotfix/<description>` | `hotfix/doctor-validation-fix` | Production fixes |

### 13.3 Integration with Existing TFCs

* **TFC-0001:** Repository layout remains unchanged
* **TFC-0002:** Commit metadata integrates with run schemas
* **TFC-0003:** Run execution records development context
* **TFC-0004:** Dataset versions trace to development commits
* **TFC-0005:** Model registry includes development metadata
* **TFC-0006:** Enhanced validation rules for workflow compliance
* **TFC-0007:** Dashboard displays development context
* **TFC-0008:** Release signing integrates with artifact signing

This TFC completes the development lifecycle management by adding **rigorous, ML-focused workflow controls** that ensure **full traceability**, **strict validation**, and **seamless integration** with the existing ProjectStrataML framework.

---

A development workflow that passes TFC-0009 validation is considered **fully compliant** with the ProjectStrataML framework and ready for **production ML operations**.