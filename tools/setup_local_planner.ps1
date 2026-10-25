param(
  [switch]$Uninstall,
  [switch]$InstallExecution
)
$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$config = Get-Content (Join-Path $repo ".agents\planner\config.json") -Raw | ConvertFrom-Json
$prefix = "skl-SF-LocalPlanner-"
$execPrefix = "skl-SF-LocalRunner-"
if ($Uninstall) {
  Get-ScheduledTask -TaskName "$prefix*" -ErrorAction SilentlyContinue |
    Unregister-ScheduledTask -Confirm:$false
  Get-ScheduledTask -TaskName "$execPrefix*" -ErrorAction SilentlyContinue |
    Unregister-ScheduledTask -Confirm:$false
  Write-Host "Removed all skl-SF planner and execution schedules; repo data untouched."
  exit 0
}
if (-not (Get-Command "claude" -ErrorAction SilentlyContinue)) { throw "claude CLI missing" }
if (-not (Get-Command "codex" -ErrorAction SilentlyContinue)) { throw "codex CLI missing" }
if (-not (Get-Command "py" -ErrorAction SilentlyContinue)) { throw "Python launcher py missing" }
if (-not (Get-Command "gh" -ErrorAction SilentlyContinue)) { throw "GitHub CLI gh missing" }
if ($InstallExecution) {
  if (-not $config.execution_enabled -or -not $config.supervised_e2e_passed) {
    throw "Execution remains disabled until a supervised end-to-end task is approved."
  }
  if ((Get-TimeZone).Id -notin @("W. Europe Standard Time", "Central European Standard Time")) {
    throw "Set Windows timezone to Europe/Berlin before installing automatic execution."
  }
  $exe = (Get-Command powershell.exe).Source
  $script = Join-Path $repo "tools\run_local_agent.ps1"
  foreach ($name in @("claude","codex")) {
    $taskName = "$execPrefix$name"
    $delay = if ($name -eq "claude") { 5 } else { 20 }
    $action = New-ScheduledTaskAction -Execute $exe -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$script`" -Agent $name" -WorkingDirectory $repo
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes($delay) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
    $principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 3) -MultipleInstances IgnoreNew
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
    Write-Host "Registered supervised-approved hourly worker: $taskName"
  }
  Write-Host "Execution scheduler installed under logged-in subscription user; Uninstall stops both runner and planner."
  exit 0
}
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
