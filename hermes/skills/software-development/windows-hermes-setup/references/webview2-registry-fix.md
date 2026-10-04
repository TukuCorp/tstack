# WebView2 Runtime — Registry Fix for Missing Installation Detection

Some Hermes components (desktop GUI, Electron wrappers) check for WebView2 Runtime
by looking at the registry key:

```
HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}\pv
```

If WebView2 is physically installed at `C:\Program Files (x86)\Microsoft\EdgeWebView\Application\<version>\`
but the registry key is missing, tools report "WebView2 is not installed."

## Check if installed

```powershell
# Registry check
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -Name pv

# Physical files check
Get-ChildItem 'C:\Program Files (x86)\Microsoft\EdgeWebView\Application\'
```

## Fix the registry

The `pv` value should match the installed version folder name (e.g. `149.0.4022.80`).

Save as `fix_webview2.ps1` and run **as Administrator** (needs HKLM access):

```powershell
$regPath = "HKLM:\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"

if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}

Set-ItemProperty -Path $regPath -Name "pv" -Value "149.0.4022.80"
Write-Output "WebView2 registry fixed"
```

## Install WebView2 if missing

If WebView2 is actually not installed (no `Application` folder):

```bash
# Download the Evergreen Runtime bootstrapper
curl -L -o ~/Downloads/MicrosoftEdgeWebView2Setup.exe \
  "https://go.microsoft.com/fwlink/p/?LinkId=2124703"

# Run silently
~/Downloads/MicrosoftEdgeWebView2Setup.exe /silent
```

The `/silent` flag installs without UI. The `/install` flag is **not** valid for
this installer (will return exit code 87).
