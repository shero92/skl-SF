param(
  [Parameter(Mandatory=$true)][ValidateSet("claude","codex")][string]$Agent
)
$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
# Scheduled runs only report LastTaskResult; keep the runner's own stdout/stderr here.
$log = Join-Path $repo ".agents\monitoring\.local\runner-$Agent.log"
New-Item -ItemType Directory -Force (Split-Path $log) | Out-Null
if ((Test-Path $log) -and (Get-Item $log).Length -gt 1MB) { Move-Item $log "$log.1" -Force }
Push-Location $repo
try {
  Add-Content -Path $log -Encoding utf8 -Value "=== $(Get-Date -Format o) run-next $Agent ==="
  $env:PYTHONIOENCODING = "utf-8"
  # Shared entrypoint uses the same repository lease as manual sessions.
  & (Join-Path $PSScriptRoot "run_agents_manual.ps1") -Agents @($Agent) *>> $log
  $code = $LASTEXITCODE
  Add-Content -Path $log -Encoding utf8 -Value "=== exit $code ==="
  if ($code -ne 0) { throw "Local agent runner failed ($code); see $log" }
}
finally { Pop-Location }
