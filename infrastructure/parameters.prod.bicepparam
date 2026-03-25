// Production environment parameters
using './main.bicep'

param location = 'eastus'
param environment = 'prod'
param appName = 'python-devops-ref-app'
param acrSku = 'Premium'
param appServiceSku = 'P1V2'
param enableAuth = true
param createKeyVault = true
param createStorageAccount = true

param tags = {
  environment: 'production'
  project: 'python-devops-reference'
  createdBy: 'bicep'
  costCenter: 'operations'
  criticality: 'high'
}
