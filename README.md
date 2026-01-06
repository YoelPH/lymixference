Repository to reproduce the analysis for the mixture-model paper.

This repo contains:
- a DVC pipeline (`dvc.yaml` + `params.yaml`) to build the analysis artifacts, and
- precomputed results for the 2/3/4-component mixture models under `histories/` and `plots/`.

The long-running parts (bootstrap + refitting) can take a long time. The current Git state
therefore includes already-computed outputs for multiple variants.

## Quickstart

### 1) Create an environment

From the `lymixference/` folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

### 2) (Optional) Verify the pipeline is wired correctly

This prints the DAG and the configured stages:

```bash
dvc dag
dvc status
```

## What is in here

### Data products

The pipeline produces intermediate data tables under `data/`:
- `data/joined_*.csv`: concatenated multi-cohort dataset
- `data/enhanced_*.csv`: harmonized modalities / cleaned structure
- `data/filtered_*.csv`: restricted to selected anatomical subsites and reduced ICDs

In the current repo state, the `dvc.yaml` stages are configured for the 4-component setup
(e.g. `data/joined_4.csv`, `data/filtered_4.csv`).

### Model outputs

For each model variant we store fitted parameters and bootstrap refits under:
- `histories/2/` (2 components)
- `histories/3/` (3 components)
- `histories/4/` (4 components)

Each contains:
- `original_fit/`: the optimum fit on the filtered dataset
- `resampling/`: results from bootstrap refitting

Key plots used for the paper are under `plots/` and include for example:
- `plots/mixture_matrix_2_comp.{png,svg}`
- `plots/mixture_matrix_3_comp.{png,svg}`
- `plots/mixture_matrix_4_comp.{png,svg}`
- `plots/mixture_comp_uncertainty_2_comp.{png,svg}`
- `plots/mixture_comp_uncertainty_3_comp.{png,svg}`
- `plots/mixture_comp_uncertainty_4_comp.{png,svg}`

## Reproducing results

### A) Reproduce *only the lightweight parts* (minutes)

If you want to rebuild only the data preprocessing stages:

```bash
dvc repro filter
```

This will run `join → enhance → filter` and create `data/filtered_4.csv` (as currently configured).

### B) Full reproduction from scratch (can take weeks)

The stages `bootstrap` and `refitting` can be very time consuming.
To run the full pipeline:

```bash
dvc repro
```

### C) Use the existing precomputed results (recommended)

If your goal is to inspect/plot/evaluate what is already in the repository, you do not need to
run `dvc repro`.

Typical entry points:
- 4-component evaluation notebook: `4_comp_evaluation.ipynb`
- fitted params for 4 components: `histories/4/original_fit/optimal_params.csv`
- bootstrap optimal params for 4 components: `histories/4/resampling/optimal_params/`

## Notes on DVC + Git

At the moment, this repository is intended as an *interim results snapshot* for the paper.
If you plan to publish very large artifacts, prefer storing them via DVC remotes or release
archives; Git should keep the pipeline definition and small, reviewable outputs.

## Current pipeline limitation (and intended direction)

Right now, the DVC pipeline files (`dvc.yaml`, `params.yaml`) are configured primarily for the
4-component variant (e.g. `data/joined_4.csv`, `data/filtered_4.csv`, and plot names like
`*_4_comp`). This is why the repository already contains *multiple* result folders (`histories/2`,
`histories/3`, `histories/4`) even though the pipeline definition currently “points at 4”.

The intended direction (to avoid editing files between runs) is:
- introduce a run key (e.g. `general.run_name`) and derive all paths from it, and
- register already-computed outputs for older runs using `dvc commit` (which records hashes in
	`dvc.lock` without re-running commands).

This refactor is not required to use the existing results in this snapshot, but it makes future
2/3/4-component runs and publication cleaner.
