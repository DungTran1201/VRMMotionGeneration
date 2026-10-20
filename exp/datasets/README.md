# `exp/datasets/` — Dataset Policy & Storage Directory

> **Policy Notice: No Datasets Committed to Version Control**  
> Raw motion capture datasets (such as BONES-SEED, AMASS, HumanML3D) must **never** be committed to Git.

## Purpose
Serves as the local mount or storage target for motion datasets, and documents dataset sources, schema structures, provenance, and licenses.

## What Belongs Here
- Markdown documentation detailing dataset download procedures, licensing terms, and split conventions.
- Small synthetic verification schemas.

## What Must NOT Belong Here
- Raw binary motion datasets (`.npy`, `.h5`, `.tar`, `.zip`).
- Proprietary or uncredited datasets.

## Source-of-Truth Relationship
- Dataset definitions and licenses must be referenced in experiment reports in `exp/reports/`.
