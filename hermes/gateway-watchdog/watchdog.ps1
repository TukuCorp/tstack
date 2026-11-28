# Hermes gateway external watchdog. Runs every few minutes from the Hermes_Gateway_Watchdog task.
# The vendor launcher (Hermes_Gateway.vbs) exits right after spawning python, so Task Scheduler's
# RestartOnFailure never sees the gateway die. This script fills that gap. It lives outside
# gateway-service/ because `hermes update` rewrites the vendor launchers.
param([string]$HermesHome = "$env:LOCALAPPDATA\hermes", [switch]$DryRun)
$ErrorActionPreference = 'Stop'
$Log        = Join-Path $HermesHome 'logs\gateway-watchdog.log'
$Lifecycle  = Join-Path $HermesHome 'state\gateway.lifecycle.json'
$Heartbeat  = Join-Path $HermesHome 'state\gateway.heartbeat'
$History    = Join-Path $HermesHome 'logs\gateway-watchdog-restarts.txt'
$StaleMinutes = 15   # gateway writes a heartbeat every ~30s and self-exits (75) after 3 missed probes
$MaxRestarts  = 3    # per 30 minutes, so a crash loop doesn't spin forever
$BootGraceMin = 3    # don't judge a gateway that just started

function Write-Log($msg) {
    "$((Get-Date).ToString('s')) $msg" | Out-File -FilePath $Log -Append -Encoding utf8
}

function Restart-Gateway($why, [int]$killPid = 0) {
    $now = Get-Date
    $recent = @()
    if (Test-Path $History) {
        $recent = @(Get-Content $History | Where-Object { $_ -and ([datetime]$_) -gt $now.AddMinutes(-30) })
    }
    # A fresh gateway takes ~20s to claim the lifecycle file; don't fire again while it boots.
    if ($recent.Count -and ([datetime]$recent[-1]) -gt $now.AddMinutes(-$BootGraceMin)) { return }
    if ($recent.Count -ge $MaxRestarts) {
        Write-Log "SKIP restart ($why): $($recent.Count) restarts in last 30 min, crash loop suspected"
        return
    }
    if ($DryRun) { Write-Log "DRYRUN would restart ($why) kill=$killPid"; return }
    if ($killPid) { try { Stop-Process -Id $killPid -Force -ErrorAction Stop } catch {} ; Start-Sleep 3 }
    # Vendor path: the scheduled task carries the right env (HERMES_HOME, PYTHONPATH, venv).
    $out = & schtasks.exe /Run /TN Hermes_Gateway 2>&1
    @($recent + $now.ToString('s')) | Set-Content $History -Encoding utf8
    Write-Log "RESTART ($why): $out"
}

# Leave the gateway alone while `hermes update` holds its fence.
if (Test-Path (Join-Path $HermesHome '.hermes-update-in-progress')) { exit 0 }
if (-not (Test-Path $Lifecycle)) { exit 0 }

$state = Get-Content $Lifecycle -Raw | ConvertFrom-Json
$procAlive = $false
if ($state.pid) {
    $p = Get-Process -Id $state.pid -ErrorAction SilentlyContinue
    $procAlive = [bool]($p -and $p.ProcessName -like 'python*')
}

if ($state.phase -eq 'exited') {
    # exit 0/null = graceful (`hermes gateway stop`, shutdown): respect it. Non-zero (75 = watchdog) = restart.
    if ($state.exit_code -and $state.exit_code -ne 0) {
        Restart-Gateway "exited code $($state.exit_code) reason $($state.exit_reason) at $($state.exited_at)"
    }
    exit 0
}

if ($state.phase -eq 'running') {
    if (-not $procAlive) {
        Restart-Gateway "pid $($state.pid) gone without clean exit (killed/crashed)"
        exit 0
    }
    $started = [datetime]$state.started_at
    if ((Get-Date).ToUniversalTime() -lt $started.ToUniversalTime().AddMinutes($BootGraceMin)) { exit 0 }
    if (Test-Path $Heartbeat) {
        $age = ((Get-Date) - (Get-Item $Heartbeat).LastWriteTime).TotalMinutes
        if ($age -gt $StaleMinutes) {
            Restart-Gateway ("heartbeat stale {0:N0} min, pid {1} alive but wedged" -f $age, $state.pid) $state.pid
        }
    }
}
