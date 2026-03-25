// Staging environment parameters
using './main.bicep'

param location = 'eastus'
param environment = 'staging'
param appName = 'python-devops-ref-app'
param acrSku = 'Standard'
param appServiceSku = 'B2'
param enableAuth = true
param createKeyVault = true
param createStorageAccount = true

param tags = {
  environment: 'staging'
  project: 'python-devops-reference'
  createdBy: 'bicep'
  costCenter: 'engineering'
}
