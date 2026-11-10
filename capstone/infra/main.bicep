targetScope = 'resourceGroup'
resource gateway 'Microsoft.ApiManagement/service@2022-08-01' existing = {
  name: 'apim-capstone-ogkt6aocynyqw'
}
resource api 'Microsoft.ApiManagement/service/apis@2022-08-01' existing = {
  parent: gateway
  name: 'capstone-agent'
}
resource insights 'Microsoft.Insights/components@2020-02-02' existing = {
  scope: resourceGroup('func-agent-ticket-tools-001_group')
  name: 'func-agent-ticket-tools-001'
}
var httpLogging = {
  request: { headers: [], body: { bytes: 0 } }
  response: { headers: [], body: { bytes: 0 } }
}
resource logger 'Microsoft.ApiManagement/service/loggers@2022-08-01' = {
  parent: gateway
  name: 'capstone-appinsights'
  properties: {
    loggerType: 'applicationInsights'
    resourceId: insights.id
    isBuffered: true
    credentials: { instrumentationKey: insights.properties.InstrumentationKey }
  }
}
resource diagnostics 'Microsoft.ApiManagement/service/apis/diagnostics@2022-08-01' = {
  parent: api
  name: 'applicationinsights'
  properties: {
    loggerId: logger.id
    alwaysLog: 'allErrors'
    sampling: { samplingType: 'fixed', percentage: 100 }
    httpCorrelationProtocol: 'W3C'
    logClientIp: false
    frontend: httpLogging
    backend: httpLogging
  }
}
resource trafficAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'capstone-gateway-traffic'
  location: 'global'
  properties: {
    description: 'Gateway traffic exceeds 50 requests in five minutes; no notification action attached.'
    severity: 2
    enabled: true
    scopes: [gateway.id]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    autoMitigate: true
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [{
        name: 'GatewayTraffic'
        metricNamespace: 'Microsoft.ApiManagement/service'
        metricName: 'Requests'
        operator: 'GreaterThan'
        threshold: 50
        timeAggregation: 'Total'
        criterionType: 'StaticThresholdCriterion'
      }]
    }
    actions: []
  }
}
output gatewayUrl string = gateway.properties.gatewayUrl
