// Development environment parameters
using './main.bicep'

param location = 'eastus'
param environment = 'dev'
param appName = 'python-devops-ref-app'
param acrSku = 'Basic'
param appServiceSku = 'B1'
param enableAuth = false
param createKeyVault = false
param createStorageAccount = false

param tags = {
  environment: 'development'
  project: 'python-devops-reference'
  createdBy: 'bicep'
  costCenter: 'engineering'
}
