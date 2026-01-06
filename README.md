# lymixference — reproduction package for the mixture-model paper

This repository is a **reproducible snapshot** for our paper.

It contains:
- a **DVC pipeline** (see `dvc.yaml` + `params.yaml`) to rebuild analysis artifacts, and
- **precomputed outputs** committed to Git for the 2/3/4-component mixture models (so you can inspect results immediately).

The long-running parts are **bootstrap + refitting** and can be very time consuming. For that reason, this repo ships already computed outputs under `histories_precomputed/` and plots under `plots_precomputed/`.

If you want to reproduce everything from scratch, you can do so via DVC.

The most important Figures regarding the 4 component model are in the notebook `4_comp_evaluation.ipynb` and ready to be reproduced or to be adapted to explore other predictions.

## Quickstart

From the `lymixference/` folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

Optional sanity checks:

```bash
dvc dag
dvc status
```

## Reproducing results with DVC

### A) Reproduce only preprocessing (minutes)

Runs `join → enhance → filter` and creates `data/filtered_<K>.csv`.

```bash
dvc repro filter
```

### B) Full reproduction from scratch (can take days/weeks)

This includes `bootstrap` and `refitting`:

```bash
dvc repro
```

### C) Use the precomputed snapshot (recommended)

You can inspect the repository outputs without running DVC.

Typical entry points:
- `4_comp_evaluation.ipynb`
- `histories_precomputed/<K>/original_fit/optimal_params.csv`
- `histories_precomputed/<K>/resampling/` (bootstrap refits)
- `plots_precomputed/` (paper plots)

## What gets produced

### Data products

The pipeline produces intermediate data tables under `data/`:

- `data/joined_<K>.csv`: concatenated multi-cohort dataset
- `data/enhanced_<K>.csv`: harmonized modalities / cleaned structure
- `data/filtered_<K>.csv`: filtered to configured anatomical subsites and reduced ICDs

Where `<K>` is the number of mixture components.

### Model outputs

For each variant, the main outputs live under:

- `histories/2/`
- `histories/3/`
- `histories/4/`

Each contains:

- `original_fit/`: optimum fit on the filtered dataset
- `resampling/`: bootstrap refits

Important plots used in the paper are written to `plots/`, for example:

- `plots/mixture_matrix_<K>_comp.{png,svg}`
- `plots/mixture_comp_uncertainty_<K>_comp.{png,svg}`
- `plots/simplex_<K>_comp.{png,svg}` (see simplex note below)

## Changing the number of components (K): edit `params.yaml`

The pipeline is parameterized via `params.yaml`.

When you change the number of mixture components $K$, **you must update multiple keys** so that:

- the DVC stages write to the right `<K>`-suffixed data files, and
- the fitting/bootstrapping stages read/write from the matching `histories/<K>/…` paths.

### Required edits in `params.yaml` (highlighted)

For a given $K \in \{2,3,4\}$, make *all* of the following consistent:

1) **Component count**
- `model.num_components: <K>`

2) **Input data path used by fitting + bootstrap**
- `general.data: data/filtered_<K>.csv`

3) **History directory used by fitting outputs**
- `general.history_dir: histories/<K>`
- `fitting.folder_path: histories/<K>/original_fit`

4) **Bootstrap folder + output paths**
- `sampling.folder_path: data/bootstrap_<K>`
- `sampling.output_path: histories/<K>/resampling`
- `sampling.starting_points: histories/<K>/original_fit/optimal_params.csv`

5) **Locations included (must be updated when K changes)**
- `data.locations: ...`

### Location sets used in this repository

This snapshot uses the following mapping between $K$ and included anatomical subsites:

- **K = 2**: `oral_cavity oropharynx`
- **K = 3**: `oral_cavity oropharynx hypopharynx` (adds **hypopharynx**)
- **K = 4**: `oral_cavity oropharynx hypopharynx larynx` (adds **larynx**)

### Example: configure K=4

In `params.yaml`, set:

```yaml
general:
	data: data/filtered_4.csv
	history_dir: histories/4

data:
	locations: oral_cavity oropharynx hypopharynx larynx

model:
	num_components: 4

fitting:
	folder_path: histories/4/original_fit

sampling:
	folder_path: data/bootstrap_4
	output_path: histories/4/resampling
	starting_points: histories/4/original_fit/optimal_params.csv
```

Then run:

```bash
dvc repro
```

## Simplex plot note

The `plot-simplex` stage exists in `dvc.yaml`, but simplex plots are only meaningful/available for **2 and 3 components**, not for 4.
If you run the full pipeline for **K=4**, you may want to skip that stage:

```bash
dvc repro --exclude plot-simplex
```

## Notes on DVC + Git

This repo is intended as a paper reproduction snapshot:

- Git tracks the pipeline definition and the precomputed artifacts committed alongside it.
- DVC provides a way to re-run the full workflow from the included data.

If you plan to distribute very large artifacts long-term, prefer DVC remotes or release archives.
