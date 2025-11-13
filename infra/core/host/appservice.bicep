param name string
param location string = resourceGroup().location
param tags object = {}

param appServicePlanId string
param runtimeName string
param runtimeVersion string
param appCommandLine string = ''
param appSettings object = {}

resource appService 'Microsoft.Web/sites@2022-03-01' = {
  name: name
  location: location
  tags: tags
  kind: 'app,linux'
  properties: {
    serverFarmId: appServicePlanId
    siteConfig: {
      linuxFxVersion: '${runtimeName}|${runtimeVersion}'
      appCommandLine: appCommandLine
      alwaysOn: true
      ftpsState: 'FtpsOnly'
      minTlsVersion: '1.2'
      appSettings: [for setting in items(appSettings): {
        name: setting.key
        value: setting.value
      }]
    }
    httpsOnly: true
  }
}

output id string = appService.id
output name string = appService.name
output uri string = 'https://${appService.properties.defaultHostName}'
