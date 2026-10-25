param(
  [Parameter(Mandatory=$true)][ValidateSet("claude","codex")][string]$Agent
)
$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $repo
try {
  & py -3 (Join-Path $repo "tools\agent_runner.py") --run-next $Agent
  if ($LASTEXITCODE -ne 0) { throw "Local agent runner failed ($LASTEXITCODE); review task evidence and locks." }
}
finally { Pop-Location }
