param(
  [Parameter(Mandatory=$true)][ValidateSet("claude","codex")][string]$Agent
)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $root
try {
  & py -3 (Join-Path $root "tools\local_planner.py") --agent $Agent
  if ($LASTEXITCODE -ne 0) { throw "Local planner exited with $LASTEXITCODE" }
}
finally { Pop-Location }
