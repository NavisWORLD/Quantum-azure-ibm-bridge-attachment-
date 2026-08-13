param(
    [string]$BaseUrl = "http://127.0.0.1:8766"
)

$health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get
if ($health.status -ne "ok") {
    throw "QBT health contract failed"
}

$sampleBody = @{
    provider = "simulator"
    shots = 128
    seed = 7
} | ConvertTo-Json
$sample = Invoke-RestMethod -Uri "$BaseUrl/v1/sample" -Method Post -ContentType "application/json" -Body $sampleBody
if ($sample.packet.active_sources -ne 1) {
    throw "QBT sample contract failed"
}

$normalizeBody = @{
    provider = "powershell"
    backend = "smoke"
    mode = "simulator"
    counts = @{ "0" = 64; "1" = 64 }
    shots = 128
} | ConvertTo-Json -Depth 4
$normalized = Invoke-RestMethod -Uri "$BaseUrl/v1/normalize" -Method Post -ContentType "application/json" -Body $normalizeBody
if ([math]::Abs([double]$normalized.state.entropy - 1.0) -gt 1e-12) {
    throw "QBT normalize contract failed"
}

Write-Host "PowerShell QBT smoke: OK"
