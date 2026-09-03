$ErrorActionPreference = 'Stop'
$api = 'http://localhost:8000'
$login = Invoke-RestMethod -Method Post -Uri "$api/v1/auth/demo-login" -Headers @{ 'X-API-Key' = 'mobius-victim-demo' }
$headers = @{ Authorization = "Bearer $($login.access_token)" }
$health = Invoke-RestMethod -Uri "$api/health"
$risk = Invoke-RestMethod -Uri "$api/v1/targets/demo-target/risk" -Headers $headers
$graph = Invoke-RestMethod -Uri "$api/v1/targets/demo-target/graph" -Headers $headers
$video = Invoke-RestMethod -Method Post -Uri "$api/v1/analyze-video" -Headers $headers
if ($health.status -ne 'ok' -or -not $risk.stage -or $graph.persistence -ne 'neo4j_incremental' -or $video.status -ne 'simulated') { throw 'P4 integration verification failed' }
[pscustomobject]@{ health = $health.status; stage = $risk.stage; graph = $graph.persistence; video = $video.status } | ConvertTo-Json -Compress
