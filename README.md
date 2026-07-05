# DevopsMlopsFinal

By Noah Hemon, Antoine Iglesias-Tallon and Nassim Ainine.

A small ML web app that predicts California housing prices. The point of the project isn't the model itself (it's a plain linear regression) but the pipeline around it: data versioning, experiment tracking, a model registry, automated quality gates, and CI/CD that promotes a model from training all the way to production.

## Stack

- **Data**: scikit-learn's California housing dataset, tracked with DVC, stored on DagsHub
- **Training / tracking**: scikit-learn + MLflow, experiments and model registry hosted on DagsHub
- **Backend**: FastAPI, serves predictions from whatever model is currently in the registry
- **Frontend**: React (Vite)
- **CI/CD**: GitHub Actions, three pipelines (see below)
- **Containers**: Docker for both backend and frontend, `docker-compose` for local runs
- **Monitoring**: Prometheus scraping a `/metrics` endpoint on the backend, Grafana dashboard on top

## Architecture

```
                    ┌──────────────┐
                    │   Frontend    │
                    │  (React/Vite) │
                    └──────┬───────┘
                           │ POST /predict
                           ▼
                    ┌──────────────┐        ┌────────────────────┐
                    │   Backend     │◄───────│   /metrics          │
                    │  (FastAPI)    │        │   scraped by         │
                    └──────┬───────┘        │   Prometheus →       │
                           │ loads model    │   Grafana dashboard  │
                           ▼                └────────────────────┘
                 ┌───────────────────┐
                 │  MLflow Registry   │
                 │  (DagsHub)         │
                 │  alias: production │
                 └─────────▲─────────┘
                           │ promote (after quality gate passes)
                 ┌───────────────────┐
                 │  MLflow Registry   │
                 │  alias: staging    │
                 └─────────▲─────────┘
                           │ register
                 ┌───────────────────┐
                 │  training/train.py │
                 │  logs run to MLflow│
                 │  (tags: git commit,│
                 │   DVC data version)│
                 └─────────▲─────────┘
                           │ reads
                 ┌───────────────────┐
                 │  data/raw/*.csv    │
                 │  tracked by DVC,   │
                 │  stored on DagsHub │
                 └───────────────────┘
```

Everything on the left (frontend → backend → model in registry) is what runs live. Everything on the right/bottom (training → registry → promotion) is the pipeline that produces the model the backend ends up serving.

## CI/CD

There are three GitHub Actions workflows, matching the three stages of the branching model (`feature/* → dev → staging → main`).

**`ci-dev.yml`** — runs on every PR into `dev`. Installs backend dependencies, runs the unit tests and integration tests, then builds (but doesn't push) both Docker images. This is the gate that has to pass before anything gets into `dev`.

**`ci-staging.yml`** — runs on push to `staging`. Runs the full test suite again, then runs the quality gate script (`training/quality_gate.py`) against whatever model is currently aliased `staging` in the registry. If that passes, it builds and pushes both Docker images to GHCR tagged `:staging`, and deploys them.

**`ci-production.yml`** — runs on push to `main`. Runs the quality gate again, and only if it passes does it run `training/promote_model.py` to move the model from the `staging` alias to `production`, then builds, pushes, and deploys the `:production` images. If the gate fails, nothing downstream runs — production stays untouched.

## Model promotion pipeline

1. `training/train.py` trains a model on the DVC-tracked dataset and logs the run to MLflow: parameters, metrics (`rmse`, `r2`), the model artifact, and two tags — the git commit and the DVC data hash — so any run can be traced back to the exact code and data that produced it.
2. `training/register_model.py` finds the best run in the experiment (lowest `rmse`), registers it as a new version of `california-housing-model`, and aliases that version `staging`.
3. `training/quality_gate.py` checks the `staging` model's `rmse` against a threshold and exits pass/fail. This is what both the staging and production pipelines call before doing anything else.
4. `training/promote_model.py` re-aliases the same version from `staging` to `production` — this only runs after the gate passes on `main`.
5. The backend loads its model at startup from the registry via `get_production_model()`.

## Monitoring

The backend exposes a `/metrics` endpoint (request count, request latency, failed requests, health status). Prometheus is configured to scrape that endpoint on the production backend, and a Grafana dashboard is built on top of it showing request volume, latency, error rate, and health status over time. Access details for the dashboard are environment-specific and set up alongside the production deployment.

## Reproducibility

Clone the repo, then:

```bash
pip install -r requirements.txt
dvc pull                      # fetches the exact tracked dataset from DagsHub
cp .env.example .env          # fill in your own MLflow/DagsHub credentials
python training/train.py           # trains a model, logs a new run to MLflow
python training/register_model.py  # registers the best run, aliases it "staging"
python training/quality_gate.py    # checks it against the rmse threshold
```

To run the whole app locally:

```bash
docker compose up --build
```

This builds and starts both the backend (port 8000) and frontend (port 5173) containers, with the backend loading whatever model is currently in the registry.
