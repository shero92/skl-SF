<#
.SYNOPSIS  Start / status / stop the Aider task worker (background, no interactive window needed).
.EXAMPLE   powershell.exe -NoProfile -File tools\run_aider_worker.ps1 start
Commands: start | run (foreground loop, used by the Scheduled Task) | status | stop | resume
The API key is never read here; Aider inherits it from the user's environment.
#>
param([Parameter(Position = 0)][ValidateSet('start', 'run', 'status', 'stop', 'resume')][string]$Command = 'status')
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Worker = Join-Path $PSScriptRoot 'aider_worker.py'
$Py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Py) { $Py = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $Py) { throw 'Python not found on PATH' }
$LogDir = Join-Path $Root '.agents\monitoring\.local\aider'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

switch ($Command) {
    'start' {
        $task = Get-ScheduledTask -TaskName 'SklSfAiderWorker' -ErrorAction SilentlyContinue
        if ($task) { Start-ScheduledTask -TaskName 'SklSfAiderWorker'; 'Scheduled task started.'; break }
        # Not installed: detached hidden background process (still no interactive window needed).
        $out = Join-Path $LogDir 'worker.out.log'; $err = Join-Path $LogDir 'worker.err.log'
        Start-Process -FilePath 'powershell.exe' -WindowStyle Hidden -WorkingDirectory $Root `
            -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath, 'run') `
            -RedirectStandardOutput $out -RedirectStandardError $err | Out-Null
        'Worker launched in background.'
    }
    'run'    { Set-Location $Root; & $Py $Worker run; exit $LASTEXITCODE }
    'status' { Set-Location $Root; & $Py $Worker status }
    'stop'   { Set-Location $Root; & $Py $Worker stop }
    'resume' { Set-Location $Root; & $Py $Worker resume }
}
