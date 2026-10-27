[CmdletBinding()]
param(
    [string[]]$Agents = @("codex", "claude"),
    [ValidateRange(1, 1000)][int]$MaxTasks = 10,
    [ValidateRange(0.01, 1440)][double]$MaxMinutes = 150,
    [switch]$IncludeArt,
    [switch]$DryRun
)
$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$selected = @((($Agents -join ",").Split(",")) | ForEach-Object { $_.Trim().ToLowerInvariant() })
if ($selected.Count -eq 0 -or @($selected | Select-Object -Unique).Count -ne $selected.Count) {
    throw "Choose unique agents: codex, claude"
}
foreach ($name in $selected) {
    if ($name -notin @("codex", "claude")) { throw "Unsupported agent: $name" }
}
$python = Get-Command py -ErrorAction Stop
$runnerArguments = @("-3", (Join-Path $PSScriptRoot "manual_agents.py"), "--source", $repo, "--agents")
$runnerArguments += $selected
$runnerArguments += @("--max-tasks", "$MaxTasks", "--max-minutes", $MaxMinutes.ToString([Globalization.CultureInfo]::InvariantCulture))
if ($IncludeArt) { $runnerArguments += "--include-art" }
if ($DryRun) { $runnerArguments += "--dry-run" }
& $python.Source @runnerArguments
if ($LASTEXITCODE -ne 0) { throw "Manual agent session failed ($LASTEXITCODE); work and evidence were preserved." }
