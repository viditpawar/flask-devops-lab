# Deployment Guide

This repository now includes real deployment flows for both GitHub Actions and Azure DevOps.

## What is automated

- Bicep infrastructure deployment (`infrastructure/main.bicep`)
- Azure Container Registry image build (`az acr build`)
- App Service configuration to use deployed image
- Post-deploy health check (`/health`)

## GitHub Actions deployment

Workflow file: `.github/workflows/python-devops.yml`

### Required GitHub secret

- `AZURE_CREDENTIALS` (service principal JSON for `azure/login`)

### Optional GitHub secrets

- `STAGING_API_KEY`
- `PRODUCTION_API_KEY`

### Optional GitHub repository variables

- `AZURE_LOCATION` (default: `eastus`)
- `AZURE_APP_NAME` (default: `python-devops-ref-app`)
- `AZURE_RESOURCE_GROUP_STAGING` (default: `rg-python-devops-staging`)
- `AZURE_RESOURCE_GROUP_PRODUCTION` (default: `rg-python-devops-prod`)

If `AZURE_CREDENTIALS` is not set, deploy jobs are skipped safely.

## Azure DevOps deployment

Pipeline file: `azure-pipelines.yml`

### Required pipeline variables

- `azureServiceConnection` (Azure Resource Manager service connection name)
- `runDeployments` set to `true`

### Helpful override variables

- `azureLocation`
- `appName`
- `stagingResourceGroup`
- `productionResourceGroup`
- `acrImageRepository`

By default, `runDeployments` is `false` to prevent accidental deploys before setup.

## Manual deployment (CLI)

```bash
az group create --name <resource-group> --location eastus

az deployment group create \
  --resource-group <resource-group> \
  --template-file infrastructure/main.bicep \
  --parameters @infrastructure/parameters.staging.bicepparam \
  --parameters appName=python-devops-ref-app dockerImageUri=python-devops-ref-app dockerImageTag=latest
```

Then build the app image into ACR:

```bash
az acr build --registry <acr-name> --image python-devops-ref-app:latest .
```

## Verify deployment

```bash
curl https://<app-hostname>/health
curl https://<app-hostname>/api/v1/hello/World
```

## Troubleshooting

- If deploy jobs skip in GitHub Actions, check `AZURE_CREDENTIALS`.
- If deploy stages skip in Azure DevOps, check `runDeployments` and `azureServiceConnection`.
- If app is unhealthy, verify `dockerImageUri` and `dockerImageTag` used in deployment.
