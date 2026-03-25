# flask-devops-lab

Small Flask API project used to practice CI/CD and Azure deployment workflows.

## What this repo is

This repo is a demo application plus delivery tooling:

- A Python/Flask web API
- Tests and lint/security checks
- Docker build support
- Azure DevOps pipeline (`azure-pipelines.yml`)
- GitHub Actions workflow (`.github/workflows/python-devops.yml`)
- Azure infrastructure template in Bicep (`infrastructure/main.bicep`)

If your question is "is this a DevOps project?", the answer is yes. It is mostly an example app wrapped in CI/CD and infrastructure automation.

## What the app does

The API is intentionally simple:

- `GET /health` returns service health and optional host metrics
- `GET /health/ready` and `GET /health/live` return readiness/liveness checks
- `GET /api/v1/hello/<name>` returns a greeting
- `POST /api/v1/hello` accepts JSON `{ "name": "..." }` and returns a greeting
- `GET /api/v1/info` returns app metadata

Extra behavior:

- Optional API-key auth for `POST /api/v1/hello` (controlled by `ENABLE_AUTH`)
- IP-based rate limiting via `flask-limiter`
- JSON logging support

## What the pipelines do today

Both pipeline definitions run the expected quality gates:

- Install dependencies
- Run flake8
- Run Bandit and pip-audit
- Run pytest with coverage
- Build and push a Docker image

Both pipelines now include real Azure deploy steps:

- Deploy Bicep infrastructure
- Build/push app image into Azure Container Registry
- Redeploy app to use the new image
- Run health check after deployment

Deployment is gated by credentials/config:

- GitHub Actions requires `AZURE_CREDENTIALS` secret (plus optional API key secrets and repo variables).
- Azure DevOps requires a valid `azureServiceConnection` and `runDeployments=true`.

## Local development

### Requirements

- Python 3.11
- pip

### Run locally

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open:

- `http://localhost:5000/health`
- `http://localhost:5000/api/v1/hello/World`

## Configuration

Configuration lives in `config.py` and environment variables.

Common variables:

- `FLASK_ENV` (`development`, `staging`, `production`)
- `ENABLE_AUTH` (`true`/`false`)
- `VALID_API_KEY`
- `LOG_LEVEL`
- `PORT`

See `.env.example` for a starter file.

## Infrastructure

`infrastructure/main.bicep` provisions:

- Azure Container Registry
- App Service Plan + Linux Web App
- Application Insights
- Optional Key Vault
- Optional Storage Account

Environment parameter files:

- `infrastructure/parameters.dev.bicepparam`
- `infrastructure/parameters.staging.bicepparam`
- `infrastructure/parameters.prod.bicepparam`

## Project layout

```text
.
|- app.py
|- config.py
|- utils.py
|- routes/
|  |- api.py
|  |- health.py
|- tests/
|- infrastructure/
|- azure-pipelines.yml
|- .github/workflows/python-devops.yml
|- docs/
```

## Notes

- Virtual environments and cache folders are intentionally ignored via `.gitignore`.
- Deployment docs are in `docs/`.
