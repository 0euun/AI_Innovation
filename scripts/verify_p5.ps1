$ErrorActionPreference = 'Stop'
$api = 'http://localhost:8000'
$victim = Invoke-RestMethod -Method Post -Uri "$api/v1/auth/demo-login" -Headers @{ 'X-API-Key' = 'mobius-victim-demo' }
$headers = @{ Authorization = "Bearer $($victim.access_token)" }
$health = Invoke-RestMethod -Uri "$api/health"
$risk = Invoke-RestMethod -Uri "$api/v1/targets/demo-target/risk" -Headers $headers
$model = Invoke-RestMethod -Uri "$api/v1/model-status"
$types = Invoke-RestMethod -Uri "$api/v1/targets/demo-target/attack-types" -Headers $headers
$graph = Invoke-RestMethod -Uri "$api/v1/targets/demo-target/graph" -Headers $headers
$evidence = curl.exe -sS -o NUL -w '%{http_code}:%{size_download}' -H "Authorization: Bearer $($victim.access_token)" "$api/v1/targets/demo-target/evidence-package"
$alerts = Invoke-RestMethod -Uri "$api/v1/targets/demo-target/alerts/history" -Headers $headers
$notifications = Invoke-RestMethod -Uri "$api/v1/targets/demo-target/notifications/history" -Headers $headers
if ($health.status -ne 'ok' -or $model.status -ne 'ready' -or -not $risk.stage -or -not $types.source -or $graph.persistence -ne 'neo4j_incremental' -or -not $evidence.StartsWith('200:')) { throw 'P5 release verification failed' }
[pscustomobject]@{ health = $health.status; model = $model.status; stage = $risk.stage; attack_model = $types.source; graph = $graph.persistence; evidence_download = $evidence; alert_history = @($alerts).Count; notification_history = @($notifications).Count } | ConvertTo-Json -Compress
