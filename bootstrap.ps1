<#
.SYNOPSIS
  Set up a Windows machine from tstack: install the tools and restore their configs.
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
    'AutoHotkey.AutoHotkey'        = { Test-Path "$env:LOCALAPPDATA\Programs\AutoHotkey\v2\AutoHotkey64.exe" }
    'DEVCOM.JetBrainsMonoNerdFont' = { [bool](Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Windows\Fonts", "$env:WINDIR\Fonts" -Filter 'JetBrainsMonoNerdFont*' -ErrorAction SilentlyContinue) }
    'ImputNet.Helium'              = { Test-Path "$env:LOCALAPPDATA\imput\Helium\Application\chrome.exe" }
}
# Tools whose official Windows install is a script (from each project's README)
$Installers = [ordered]@{
    'claude' = 'irm https://claude.ai/install.ps1 | iex'
    'codex'  = 'irm https://chatgpt.com/codex/install.ps1 | iex'
    # Herdr app (herdr-app); its installer also adds herdr-core (`hc`) when missing
    'herdr-app' = 'irm https://releases.herdr.dev/app/install.ps1 | iex'
    'hermes' = 'iex (irm https://hermes-agent.nousresearch.com/install.ps1)'
    # Antigravity CLI: full peer (rules, skills, MCP restored from agy/)
    'agy'    = 'irm https://antigravity.google/cli/install.ps1 | iex'
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
    # npm 11 skips agent-desktop's postinstall, which swaps the Node launcher for the native binary
    $ad = "$env:APPDATA\npm\node_modules\agent-desktop"
    if ((Test-Path $ad) -and -not (Select-String -Quiet 'agent-desktop-win32' "$env:APPDATA\npm\agent-desktop.cmd")) {
        Run 'agent-desktop: link native binary' { node "$ad\scripts\postinstall.js" }
    }
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

Step 'Herdr app Home toggle (AutoHotkey Startup shortcut)'
$AhkExe = "$env:LOCALAPPDATA\Programs\AutoHotkey\v2\AutoHotkey64.exe"
$AhkScript = "$HOME\.config\ahk\herdr-toggle.ahk"
$AhkLnk = Join-Path ([Environment]::GetFolderPath('Startup')) 'herdr-toggle.lnk'
if (Test-Path $AhkLnk) { Write-Host '    ok: shortcut' }
elseif ((Test-Path $AhkExe) -and (Test-Path $AhkScript)) {
    Run 'create Startup shortcut + start script' {
        $s = (New-Object -ComObject WScript.Shell).CreateShortcut($AhkLnk)
        $s.TargetPath = $AhkExe; $s.Arguments = "`"$AhkScript`""; $s.Save()
        Start-Process $AhkExe -ArgumentList "`"$AhkScript`""
    }
} else { Write-Host '    AutoHotkey or script missing; skipped' -ForegroundColor Red }

Step 'agent-browser Chrome (headless browsing)'
if (Test-Path "$HOME\.agent-browser\browsers\*") { Write-Host '    ok: agent-browser Chrome' }
elseif (Have agent-browser) { Run 'agent-browser install' { agent-browser install } }

Step 'self-contained harnesses (each loads only its own skills)'
# Opencode would otherwise also load ~/.claude/skills and ~/.claude/CLAUDE.md
if ([Environment]::GetEnvironmentVariable('OPENCODE_DISABLE_CLAUDE_CODE', 'User') -eq '1') { Write-Host '    ok: OPENCODE_DISABLE_CLAUDE_CODE' }
else { Run 'set OPENCODE_DISABLE_CLAUDE_CODE=1' { [Environment]::SetEnvironmentVariable('OPENCODE_DISABLE_CLAUDE_CODE', '1', 'User') } }
# Raise agy's automatic compaction threshold to 400k tokens
if ([Environment]::GetEnvironmentVariable('AGY_CLI_AUTO_COMPACT_OVERRIDE', 'User') -eq '400000') { Write-Host '    ok: AGY_CLI_AUTO_COMPACT_OVERRIDE' }
else { Run 'set AGY_CLI_AUTO_COMPACT_OVERRIDE=400000' { [Environment]::SetEnvironmentVariable('AGY_CLI_AUTO_COMPACT_OVERRIDE', '400000', 'User') } }
# grill-with-ui is vendored (sync skips it): git clone for Claude, plain copies for the others
$Gwu = "$HOME\.claude\skills\grill-with-ui"
if (Test-Path "$Gwu\.git") { Write-Host '    ok: grill-with-ui clone' }
elseif (Have git) { Run 'clone grill-with-ui' { git clone https://github.com/jasonku09/grill-with-ui $Gwu } }
foreach ($dst in "$HOME\.codex\skills", "$HOME\.config\opencode\skills", "$HOME\.gemini\config\skills", "$env:LOCALAPPDATA\hermes\skills\software-development") {
    if ((Test-Path "$Gwu\SKILL.md") -and (Test-Path $dst) -and -not (Test-Path "$dst\grill-with-ui")) {
        Run "copy grill-with-ui -> $dst" { robocopy $Gwu "$dst\grill-with-ui" /E /XD .git node_modules /NFL /NDL /NJH /NJS /NP | Out-Null }
    }
}

Step 'wiki (private TukuCorp/wiki -> ~/wiki)'
# Agent memory lives there, not here: tstack is public
$WikiDir = "$HOME\wiki"
$ghAuthed = (Have gh) -and (& { $ErrorActionPreference = 'Continue'; gh auth status *> $null; $LASTEXITCODE -eq 0 })
if (Test-Path "$WikiDir\.git") { Write-Host '    ok: clone' }
elseif ($ghAuthed) { Run 'gh repo clone TukuCorp/wiki ~/wiki' { gh repo clone TukuCorp/wiki $WikiDir } }
else { Write-Host '    gh not signed in; after gh auth login, re-run bootstrap' -ForegroundColor Yellow }
if ((Test-Path "$WikiDir\.git") -and (Have python)) {
    $collectArgs = @("$WikiDir\scripts\collect.py", '--restore')
    if ($DryRun) { $collectArgs += '--dry-run' }
    python @collectArgs  # fills empty Claude/Codex/Hermes memory stores only
    if (Get-ScheduledTask -TaskName 'wiki-sync' -ErrorAction SilentlyContinue) { Write-Host '    ok: wiki-sync task' }
    else { Run 'register wiki-sync task' { & "$WikiDir\scripts\install-task.ps1" } }
}

Step 'left for you'
Write-Host @'
    - Sign in: claude, codex login, gh auth login, hermes setup, opencode auth login, gws auth login, agy (personal Google account)
    - Fill the <REDACTED> values restore.py listed above (API keys, MCP env blocks)
    - Restart the Herdr app so it picks up the restored keys.json and settings.json
    - Helium is the daily browser (Chrome stays as fallback and as the source of extension updates).
      Set it as the Windows default (Settings > Default apps) and sign in to the Google accounts.
    - Extensions: add browse (chromewebstore.google.com/detail/mfnicocicmmlkpjnaffgihfjhdgjkdjg) and
      Claude to Chrome. Helium's Web Store page can render blank, so copy each from Chrome's
      User Data\Default\Extensions\<id>\<ver> to %LOCALAPPDATA%\imput\browse-ext and \claude-ext,
      delete _metadata, then helium://extensions > Developer mode > Load unpacked (the key keeps the ID).
    - Pair browse: run browse pair, then open in Helium
      chrome-extension://mfnicocicmmlkpjnaffgihfjhdgjkdjg/onboarding.html#code=<CODE>&port=19988
      Windows: if pair fails with "spawnSync browse ENOENT", set "entry" in
      ~/.config/browse/settings.json to %APPDATA%\npm\node_modules\@opencode\browse\dist\cli.mjs
    - The rule files name Helium's browse browser id and Claude in Chrome deviceId; a new machine gets
      new ones: update them from browse status and list_connected_browsers.
'@
