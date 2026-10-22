<#
.SYNOPSIS
  Set up a Windows machine from tstack: install the tools, restore their configs, reinstall herdr plugins.
  Anything already installed is skipped, so it is safe to re-run.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File bootstrap.ps1 -DryRun
  powershell -ExecutionPolicy Bypass -File bootstrap.ps1
  powershell -ExecutionPolicy Bypass -File bootstrap.ps1 -SkipInstall   # configs + plugins only
#>
param([switch]$DryRun, [switch]$SkipInstall)
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Green }
function Run($desc, [scriptblock]$cmd) {
    if ($DryRun) { Write-Host "    would: $desc" -ForegroundColor Yellow } else { Write-Host "    $desc"; & $cmd }
}
function Have($exe) {
    # The Microsoft Store stub for python.exe counts as missing
    $c = Get-Command $exe -ErrorAction SilentlyContinue | Select-Object -First 1
    [bool]$c -and $c.Source -notlike '*\WindowsApps\*'
}
function Update-SessionPath {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
}

# winget id -> test that it is already installed
$Winget = [ordered]@{
    'Git.Git'                      = { Have git }
    'GitHub.cli'                   = { Have gh }
    'OpenJS.NodeJS.LTS'            = { Have node }
    'Python.Python.3.14'           = { Have python }
    'astral-sh.uv'                 = { Have uv }
    'Oven-sh.Bun'                  = { Have bun }
    'AmanThanvi.noctty'            = { Test-Path "$env:LOCALAPPDATA\Programs\noctty" }
    'DEVCOM.JetBrainsMonoNerdFont' = { [bool](Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Windows\Fonts", "$env:WINDIR\Fonts" -Filter 'JetBrainsMonoNerdFont*' -ErrorAction SilentlyContinue) }
}
# Tools whose official Windows install is a script (from each project's README)
$Installers = [ordered]@{
    'claude' = 'irm https://claude.ai/install.ps1 | iex'
    'codex'  = 'irm https://chatgpt.com/codex/install.ps1 | iex'
    'herdr'  = 'irm https://herdr.dev/install.ps1 | iex'
    'hermes' = 'iex (irm https://hermes-agent.nousresearch.com/install.ps1)'
}

if (-not $SkipInstall) {
    Step 'winget packages'
    foreach ($id in $Winget.Keys) {
        if (& $Winget[$id]) { Write-Host "    ok: $id"; continue }
        Run "winget install $id" { winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements }
    }
    Update-SessionPath

    Step 'agent CLIs'
    foreach ($exe in $Installers.Keys) {
        if (Have $exe) { Write-Host "    ok: $exe"; continue }
        # Child process, so an installer that calls `exit` can't end this script
        Run "install $exe" { powershell -NoProfile -ExecutionPolicy Bypass -Command $Installers[$exe] }
    }
    Update-SessionPath

    Step 'global packages (machine/packages.json)'
    $pk = Get-Content "$Root\machine\packages.json" -Raw | ConvertFrom-Json
    $npmMissing = @($pk.npm | Where-Object { -not (Test-Path "$env:APPDATA\npm\node_modules\$_") })
    if ($npmMissing) { Run "npm install -g $($npmMissing -join ' ')" { npm install -g @npmMissing } } else { Write-Host '    ok: npm' }
    foreach ($p in $pk.bun) {
        if (Test-Path "$HOME\.bun\install\global\node_modules\$p") { Write-Host "    ok: $p"; continue }
        Run "bun add -g $p" { bun add -g $p }
    }
    $uvHave = if (Have uv) { (uv tool list 2>$null) -join "`n" } else { '' }
    foreach ($p in $pk.uv) {
        if ($uvHave -match "(?m)^$([regex]::Escape($p)) ") { Write-Host "    ok: $p"; continue }
        Run "uv tool install $p" { uv tool install $p }
    }
}

Step 'configs (restore.py)'
$restoreArgs = @("$Root\restore.py")
if ($DryRun) { $restoreArgs += '--dry-run' }
if (Have python) { python @restoreArgs } else { Write-Host '    python missing; install it, then run restore.py' -ForegroundColor Red }

Step 'herdr plugins'
if (Have herdr) {
    $installed = @((herdr plugin list --json | ConvertFrom-Json).result.plugins | ForEach-Object { "$($_.source.owner)/$($_.source.repo)" })
    foreach ($p in (Get-Content "$Root\herdr\plugins.json" -Raw | ConvertFrom-Json)) {
        if ($installed -contains $p.repo) { Write-Host "    ok: $($p.repo)"; continue }
        Run "herdr plugin install $($p.repo) --ref $($p.ref)" { herdr plugin install $p.repo --ref $p.ref --yes }
    }
} else { Write-Host '    herdr missing; skipped' -ForegroundColor Red }

Step 'user environment'
# chrome-devtools-axi attaches to my everyday (signed-in) Chrome instead of launching its own
$UserEnv = @{ CHROME_DEVTOOLS_AXI_AUTO_CONNECT = '1' }
foreach ($k in $UserEnv.Keys) {
    if ([Environment]::GetEnvironmentVariable($k, 'User') -eq $UserEnv[$k]) { Write-Host "    ok: $k"; continue }
    Run "set $k=$($UserEnv[$k])" { [Environment]::SetEnvironmentVariable($k, $UserEnv[$k], 'User') }
}

Step 'left for you'
Write-Host @'
    - Sign in: claude, codex login, gh auth login, hermes setup, opencode auth login, gws auth login
    - Fill the <REDACTED> values restore.py listed above (API keys, MCP env blocks)
    - Restart noctty (Ctrl+Shift+, reloads config) and herdr so they pick up the restored configs
    - Chrome: sign in to the work account, then turn on chrome://inspect/#remote-debugging (for chrome-devtools-axi)
'@
