# Deployment Guide

## Platform: Render (free tier)

### 1. Create Render account
Sign up at https://render.com with your GitHub account.

### 2. Deploy using Blueprint
1. Go to Render Dashboard → **New** → **Blueprint**
2. Connect your GitHub repo `An0maly404/DevopsMlopsFinal`
3. Render auto-detects `render.yaml` and creates:
   - `mlops-backend` (web service, port 8000)
   - `mlops-frontend` (web service, port 80)

### 3. Set up environment secrets on Render
Create a **Shared Environment Group** named `mlops-secrets`:
| Key | Value |
|-----|-------|
| `MLFLOW_TRACKING_URI` | `https://dagshub.com/noah.hemon/DevopsMLopsProject.mlflow` |
| `MLFLOW_TRACKING_USERNAME` | `noah.hemon` |
| `MLFLOW_TRACKING_PASSWORD` | `8cb0606103a4ffd2822ad447ce00fbff200b656a` |

### 4. GitHub Secrets for CI deploy hooks
In GitHub `Settings → Secrets → Actions`:
| Secret | Value |
|--------|-------|
| `RENDER_STAGING_DEPLOY_HOOK` | Render deploy hook URL for staging service |
| `RENDER_PRODUCTION_DEPLOY_HOOK` | Render deploy hook URL for production service |

Get these from Render: service → **Settings** → **Deploy Hook**.

### 5. Public URLs
After deploy:
- Frontend: `https://mlops-frontend.onrender.com`
- Backend: `https://mlops-backend.onrender.com`
- Backend health: `https://mlops-backend.onrender.com/health`

### 6. Verify end-to-end
1. Open `https://mlops-frontend.onrender.com`
2. Fill the prediction form
3. Submit — you should see a predicted house value

## Monitoring (Phase 13)
- Prometheus: configured to scrape `/metrics` from backend
- Grafana: `http://localhost:3000` (username: `admin`, password: `admin`)
