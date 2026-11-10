import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

def az(*args):
    return subprocess.check_output(['az', *args], text=True).replace(chr(65279), '').strip()

def resource(rid, version):
    return json.loads(az('rest', '--method', 'get', '--url',
        f'https://management.azure.com{rid}?api-version={version}', '-o', 'json'))

subscription = az('account', 'show', '--query', 'id', '-o', 'tsv')
root = f'/subscriptions/{subscription}/resourceGroups/rg-genai-dev-/providers'
service = root + '/Microsoft.ApiManagement/service/apim-capstone-ogkt6aocynyqw'
evidence = {'checked_at': datetime.now(timezone.utc).isoformat(), 'checks': {}}

def check(name, condition):
    evidence['checks'][name] = bool(condition)
    if not condition:
        raise RuntimeError('FAILED: ' + name)
    print('PASS: ' + name, flush=True)

def run():
    gateway = resource(service, '2022-08-01')
    check('Gateway provisioned', gateway['properties']['provisioningState'] == 'Succeeded')
    vault = resource(root + '/Microsoft.KeyVault/vaults/kv-cap-ogkt6aocynyqw', '2023-07-01')
    check('Key Vault uses Azure RBAC', vault['properties'].get('enableRbacAuthorization') is True)
    search = resource(root + '/Microsoft.Search/searchServices/search-agentic-capstone-2026', '2023-11-01')
    check('Search managed identity enabled', search.get('identity', {}).get('principalId'))
    diag = resource(service + '/apis/capstone-agent/diagnostics/applicationinsights', '2022-08-01')
    check('Gateway monitoring attached', diag['properties'].get('loggerId'))
    raw = az('rest', '--method', 'get', '--url',
        f'https://management.azure.com{service}/apis/capstone-agent/policies/policy?api-version=2022-08-01&format=rawxml', '-o', 'json')
    if raw.startswith('<'):
        policy = raw
    else:
        parsed = json.loads(raw)
        policy = parsed if isinstance(parsed, str) else parsed['properties']['value']
    check('Managed identity backend authentication configured', 'authentication-managed-identity' in policy)
    check('Gateway rate limit configured', '<rate-limit ' in policy)
    named = resource(service + '/namedValues/platform-access-key', '2022-08-01')
    check('Gateway credential references Key Vault', named['properties'].get('keyVault', {}).get('secretIdentifier'))
    check('Credential enforced by policy', '{{platform-access-key}}' in policy)
    subscription_key = az('rest', '--method', 'post', '--url',
        f'https://management.azure.com{service}/subscriptions/capstone-recording/listSecrets?api-version=2022-08-01',
        '--query', 'primaryKey', '-o', 'tsv')
    platform_key = az('keyvault', 'secret', 'show', '--vault-name', 'kv-cap-ogkt6aocynyqw',
        '--name', 'platform-access-key', '--query', 'value', '-o', 'tsv')
    def request(path, payload, key):
        req = urllib.request.Request(gateway['properties']['gatewayUrl'] + '/agent/' + path + '?api-version=v1',
            data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': subscription_key, 'X-Platform-Key': key}, method='POST')
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.load(response)
    rejected = False
    try:
        request('conversations', {}, 'deliberately-invalid')
    except urllib.error.HTTPError as error:
        evidence['invalid_credential_http_status'] = error.code
        rejected = error.code == 401
    check('Invalid gateway credential rejected with HTTP 401', rejected)
    conversation = request('conversations', {}, platform_key)
    response = request('responses', {'conversation': conversation['id'], 'input':
        'Use enterprise-policy-knowledge to retrieve the approved corporate VPN access requirements. Cite the source.'}, platform_key)
    answer = '\n'.join(content.get('text', '') for item in response.get('output', [])
        for content in (item.get('content') or []) if content.get('type') == 'output_text')
    check('Authorized agent request returned an answer', answer.strip())
    evidence['answer'] = answer
    print(answer)

Path('outputs').mkdir(exist_ok=True)
try:
    run()
except Exception as error:
    evidence['status'] = 'failed'
    evidence['error_type'] = type(error).__name__
    raise
else:
    evidence['status'] = 'passed'
finally:
    Path('outputs/platform-validation.json').write_text(json.dumps(evidence, indent=2))
