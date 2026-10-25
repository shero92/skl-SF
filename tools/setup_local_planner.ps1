param(
  [switch]$Uninstall
)
$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$config = Get-Content (Join-Path $repo ".agents\planner\config.json") -Raw | ConvertFrom-Json
$prefix = "skl-SF-LocalPlanner-"
if ($Uninstall) {
  Get-ScheduledTask -TaskName "$prefix*" -ErrorAction SilentlyContinue |
    Unregister-ScheduledTask -Confirm:$false
  Write-Host "Removed skl-SF planner schedules; repo data untouched."
  exit 0
}
if (-not (Get-Command "claude" -ErrorAction SilentlyContinue)) { throw "claude CLI missing" }
if (-not (Get-Command "codex" -ErrorAction SilentlyContinue)) { throw "codex CLI missing" }
if (-not (Get-Command "py" -ErrorAction SilentlyContinue)) { throw "Python launcher py missing" }
if (-not (Get-Command "gh" -ErrorAction SilentlyContinue)) { throw "GitHub CLI gh missing" }
$script = Join-Path $repo "tools\run_local_planner.ps1"
$exe = (Get-Command powershell.exe).Source
foreach ($entry in $config.schedule) {
  $name = "$prefix$($entry.time.Replace(':',''))-$($entry.agent)"
  $time = [DateTime]::ParseExact($entry.time, "HH:mm", [Globalization.CultureInfo]::InvariantCulture)
  $arguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File ""$script"" -Agent $($entry.agent)"
  $action = New-ScheduledTaskAction -Execute $exe -Argument $arguments -WorkingDirectory $repo
  $trigger = New-ScheduledTaskTrigger -Daily -At $time
  $principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
  $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 20) -MultipleInstances IgnoreNew
  Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
  Write-Host "Registered $name"
}
Write-Host "Runs under your logged-in Windows account; sign-in and CLI OAuth must remain valid."
