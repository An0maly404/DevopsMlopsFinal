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
                    ┌──────────────┐  /metrics   ┌────────────┐   ┌─────────┐
                    │   Backend     │────────────►│ Prometheus  │──►│ Grafana │
                    │  (FastAPI)    │             └────────────┘   └─────────┘
                    └──────┬───────┘
                           │ loads model
                           ▼
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

**`ci-dev.yml`** - runs on every PR into `dev`. Installs backend dependencies, then runs unit tests, integration tests, and the end-to-end test as separate named steps, then builds (but doesn't push) both Docker images. This is the gate that has to pass before anything gets into `dev`.

**`ci-staging.yml`** - runs on push to `staging`. Pulls the DVC-tracked dataset, trains a new candidate model (`training/train.py`), registers it (`training/register_model.py`, aliased `staging`), runs the full test suite, then runs the quality gate (`training/quality_gate.py`) against that candidate. If that passes, it builds and pushes both Docker images to GHCR tagged `:staging` and triggers a deploy to the staging service on Render.

**`ci-production.yml`** - runs on push to `main`. Runs the quality gate again, and only if it passes does it run `training/promote_model.py` to move the model from the `staging` alias to `production`, then builds, pushes, and deploys the `:production` images to Render. If the gate fails, nothing downstream runs - production stays untouched.

All three workflows read their DagsHub/MLflow credentials from GitHub Secrets (`MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, `MLFLOW_TRACKING_PASSWORD`), and the staging/production jobs each deploy to their own GitHub Environment (`staging`, `production`) with their own Render deploy hook secret - so each environment gets its own config instead of one shared set of variables.

## Model promotion pipeline

1. `training/train.py` trains a model on the DVC-tracked dataset and logs the run to MLflow: parameters, metrics (`rmse`, `r2`), the model artifact, and two tags - the git commit and the DVC data hash - so any run can be traced back to the exact code and data that produced it.
2. `training/register_model.py` finds the best run in the experiment (lowest `rmse`), registers it as a new version of `california-housing-model`, and aliases that version `staging`.
3. `training/quality_gate.py` checks the `staging` model's `rmse` against a threshold and exits pass/fail. This is what both the staging and production pipelines call before doing anything else.
4. `training/promote_model.py` re-aliases the same version from `staging` to `production` - this only runs after the gate passes on `main`.
5. The backend loads its model at startup from the registry via `get_production_model()`.

## Monitoring

The backend exposes a `/metrics` endpoint via `prometheus-fastapi-instrumentator` (request count and latency, broken down by status code) plus a custom `backend_uptime_seconds` gauge. `docker-compose.yml` runs Prometheus and Grafana alongside the app, with Prometheus scraping the backend every 5 seconds and Grafana connected to it as a data source, showing request volume, latency, error rate, and uptime.

- Prometheus UI: `http://localhost:9090`
- Grafana dashboard: `http://localhost:3000` (login: `admin` / `admin`)

This currently only runs against the local `docker-compose` stack — Prometheus's scrape target is the internal `backend:8000` service name, not the public Render backend, so it isn't monitoring the live production deployment yet. Pointing it at production would mean either deploying Prometheus/Grafana as their own Render services scraping the public backend URL, or using a hosted option like Grafana Cloud.

## Deployment

The app deploys to [Render](https://render.com) via the `render.yaml` blueprint at the repo root - one web service for the backend, one for the frontend, both built from their Dockerfiles. `ci-staging.yml` and `ci-production.yml` trigger a Render deploy hook after their respective quality gates pass. See [DEPLOY.md](DEPLOY.md) for the full setup steps (Render account, environment secrets, GitHub deploy hook secrets).

- Frontend: `https://mlops-frontend.onrender.com`
- Backend: `https://mlops-backend.onrender.com`

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

This builds and starts the backend (port 8000), frontend (port 5173), Prometheus (port 9090), and Grafana (port 3000), with the backend loading whatever model is currently in the registry.
