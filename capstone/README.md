# Enterprise Agentic AI Platform

Reuses Microsoft Foundry agent agent-it-policy-security version 6, Search
knowledge base enterprise-policy-kb, the enterprise-policy-mcp Function tool,
Key Vault kv-cap-ogkt6aocynyqw and API Management apim-capstone-ogkt6aocynyqw.
Approved source: vpn_access_policy.txt in approved-policies.

## Infrastructure
infra/main.bicep manages operational configuration on existing services:
Application Insights logging and a traffic alert (over 50 requests in five
minutes). It does not recreate the entire platform. The alert has no email
or other notification action attached.

## Validation
Run python scripts/validate_platform.py from this directory in Azure Cloud
Shell. Credentials remain hidden. Checks include managed identity and RBAC
configuration, Key Vault-backed gateway credentials, HTTP 401 rejection,
and an authorized agent response. Rate limiting is inspected, not load tested.

## Evaluation
The GitHub workflow uses Microsoft's preview evaluation tooling and an
85% task-adherence gate. With three cases, all three must pass. Missing or
incomplete evaluation results block. This small set is not comprehensive
security testing. Source files contain no actual credential values.

## Recording
Use actual workflow results and artifacts. Use monitoring.kql in the existing
Application Insights Logs window after telemetry arrives. Show secrets names
only. Do not claim success for unfinished or failed checks.

## Local files
Cloud Shell sessions are temporary. Download the ZIP after every completed
setup run. GitHub preserves the committed source and CI artifacts separately.
