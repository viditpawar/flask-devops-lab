// ================================================================================
// Python DevOps Reference App - Main Deployment Template
// ================================================================================
// This Bicep template deploys a complete Azure infrastructure for the 
// Python DevOps Reference application including:
// - Container Registry
// - App Service Plan (Linux)
// - App Service (Web App)
// - Application Insights
// - Key Vault (optional)
// - Storage Account (optional)
// ================================================================================

param location string = resourceGroup().location
param environment string = 'dev'
param appName string = 'python-devops-ref-app'

// Tags for resource management
param tags object = {
  environment: environment
  project: 'python-devops-reference'
  createdBy: 'bicep'
}

// Azure Container Registry Parameters
param acrName string = '${replace(appName, '-', '')}acr${environment}'
param acrSku string = 'Standard'

// App Service Parameters
param appServicePlanName string = '${appName}-asp-${environment}'
param appServiceName string = '${appName}-app-${environment}'
param appServiceSku string = environment == 'prod' ? 'P1V2' : 'B1'

// Application Insights Parameters
param appInsightsName string = '${appName}-ai-${environment}'

// Key Vault Parameters
param keyVaultName string = '${replace(appName, '-', '')}kv${environment}'
param createKeyVault bool = false

// Storage Account Parameters
param storageAccountName string = '${replace(appName, '-', '')}sa${environment}'
param createStorageAccount bool = false

// Docker image settings
param dockerImageUri string = ''
param dockerImageTag string = 'latest'

// Application settings
param enableAuth bool = environment != 'dev'
param apiKeyValue string = ''

// ================================================================================
// Variables
// ================================================================================

var acrLoginServer = '${acrName}.azurecr.io'
var dockerImage = !empty(dockerImageUri) ? '${acrLoginServer}/${dockerImageUri}:${dockerImageTag}' : 'nginx:latest'

// ================================================================================
// Resources
// ================================================================================

// Azure Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: acrName
  location: location
  tags: tags
  sku: {
    name: acrSku
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    RetentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  tags: tags
  sku: {
    name: appServiceSku
    capacity: environment == 'prod' ? 2 : 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// App Service (Web App)
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: appServiceName
  location: location
  tags: tags
  kind: 'app,linux,container'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    containerSize: 0
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'DOCKER|${dockerImage}'
      alwaysOn: environment == 'prod'
      http20Enabled: true
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${acrLoginServer}'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_USERNAME'
          value: acr.listCredentials().username
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
          value: acr.listCredentials().passwords[0].value
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATION_KEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'FLASK_ENV'
          value: environment
        }
        {
          name: 'ENABLE_AUTH'
          value: string(enableAuth)
        }
        {
          name: 'LOG_LEVEL'
          value: environment == 'prod' ? 'WARNING' : 'INFO'
        }
        {
          name: 'ENABLE_MONITORING'
          value: 'true'
        }
        {
          name: 'PORT'
          value: '80'
        }
      ]
    }
  }
}

// Key Vault (optional)
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = if (createKeyVault) {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enableRbacAuthorization: true
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
  }
}

// Add API Key to Key Vault (if created and apiKeyValue is provided)
resource kvApiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = if (createKeyVault && !empty(apiKeyValue)) {
  name: 'api-key'
  parent: keyVault
  properties: {
    value: apiKeyValue
  }
}

// Storage Account (optional)
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = if (createStorageAccount) {
  name: storageAccountName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: environment == 'prod' ? 'Standard_GRS' : 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

// ================================================================================
// Outputs
// ================================================================================

output appServiceUrl string = 'https://${appService.properties.defaultHostName}'
output appInsightsKey string = appInsights.properties.InstrumentationKey
output containerRegistryLoginServer string = acrLoginServer
output containerRegistryName string = acr.name
output appServicePlanId string = appServicePlan.id
output appServiceId string = appService.id
output keyVaultId string = createKeyVault ? keyVault.id : ''
output storageAccountId string = createStorageAccount ? storageAccount.id : ''
