# Fixture test for watchdog.ps1 in -DryRun mode. Each case builds a fake HERMES_HOME and checks the log.
$wd = Join-Path $PSScriptRoot 'watchdog.ps1'
# The stale/fresh-heartbeat cases need a live python PID; use the running gateway's.
$livePid = (Get-Content "$env:LOCALAPPDATA\hermes\state\gateway.lifecycle.json" -Raw | ConvertFrom-Json).pid
$old = (Get-Date).ToUniversalTime().AddHours(-1).ToString('o')
$cases = @(
  @{ name='exited 75 -> restart';        life=@{phase='exited';pid=1;exit_code=75;exit_reason='loop_liveness_watchdog'}; expect='DRYRUN would restart \(exited code 75' },
  @{ name='graceful stop -> leave';      life=@{phase='exited';pid=1;exit_code=0;exit_reason='graceful_shutdown'};      expect=$null },
  @{ name='running, pid dead -> restart'; life=@{phase='running';pid=999999;started_at=$old};                             expect='DRYRUN would restart \(pid 999999 gone' },
  @{ name='alive + stale hb -> kill';    life=@{phase='running';pid=$livePid;started_at=$old}; staleHb=$true;           expect="kill=$livePid" },
  @{ name='alive + fresh hb -> leave';   life=@{phase='running';pid=$livePid;started_at=$old};                           expect=$null },
  @{ name='restarted 1 min ago -> wait'; life=@{phase='exited';pid=1;exit_code=75}; recent=$true;                       expect=$null },
  @{ name='update in progress -> leave'; life=@{phase='exited';pid=1;exit_code=75}; marker=$true;                       expect=$null }
)
$fail = 0
foreach ($c in $cases) {
  $h = Join-Path $env:TEMP ("wdtest-" + [guid]::NewGuid())
  New-Item -ItemType Directory -Force "$h\state","$h\logs" | Out-Null
  $c.life | ConvertTo-Json | Set-Content "$h\state\gateway.lifecycle.json"
  Set-Content "$h\state\gateway.heartbeat" 'x'
  if ($c.staleHb) { (Get-Item "$h\state\gateway.heartbeat").LastWriteTime = (Get-Date).AddMinutes(-30) }
  if ($c.recent) { Set-Content "$h\logs\gateway-watchdog-restarts.txt" (Get-Date).AddMinutes(-1).ToString('s') }
  if ($c.marker) { Set-Content "$h\.hermes-update-in-progress" 'x' }
  & powershell -NoProfile -ExecutionPolicy Bypass -File $wd -HermesHome $h -DryRun
  $log = if (Test-Path "$h\logs\gateway-watchdog.log") { Get-Content "$h\logs\gateway-watchdog.log" -Raw } else { '' }
  $ok = if ($c.expect) { $log -match $c.expect } else { -not $log }
  if (-not $ok) { $fail++ }
  "{0}  {1}  | log: {2}" -f ($(if ($ok) {'PASS'} else {'FAIL'})), $c.name, $log.Trim()
  Remove-Item -Recurse -Force $h
}
"failures: $fail"
exit $fail
