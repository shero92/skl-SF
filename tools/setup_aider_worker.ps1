<#
.SYNOPSIS  Install or remove the Windows Scheduled Task for the Aider worker.
           Does nothing unless -Install/-Uninstall is passed. Run ONLY after explicit owner approval.
.EXAMPLE   powershell.exe -NoProfile -File tools\setup_aider_worker.ps1 -Install
Never touches the 'SyncAISkills' task. Never stores or reads the API key.
#>
param([switch]$Install, [switch]$Uninstall, [switch]$WhatIfOnly)
$ErrorActionPreference = 'Stop'
$TaskName = 'SklSfAiderWorker'
if ($TaskName -eq 'SyncAISkills') { throw 'refusing to touch SyncAISkills' }
$Runner = Join-Path $PSScriptRoot 'run_aider_worker.ps1'
if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    "Removed $TaskName"; return
}
if (-not $Install) { "Dry description only. Would register '$TaskName' at user logon: powershell.exe -NoProfile -File `"$Runner`" run. Pass -Install to register."; return }
$args = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Runner`" run"
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $args -WorkingDirectory (Split-Path -Parent $PSScriptRoot)
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
if ($WhatIfOnly) { 'WhatIf: would register ' + $TaskName; return }
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
"Registered $TaskName (starts at logon; the worker itself stays gated by aider_execution_enabled)."
