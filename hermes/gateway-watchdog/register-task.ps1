# Registers Hermes_Gateway_Watchdog: runs watchdog.ps1 hidden every 5 min and 3 min after logon.
# Idempotent: replaces an existing task of the same name.
$script = Join-Path $PSScriptRoot 'watchdog.ps1'
$a = New-ScheduledTaskAction -Execute 'conhost.exe' -Argument "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$script`""
$every = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5)
$logon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME; $logon.Delay = 'PT3M'
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 2)
$p = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$task = Register-ScheduledTask -TaskName Hermes_Gateway_Watchdog -Action $a -Trigger @($every, $logon) -Settings $s -Principal $p -Force `
    -Description "Restarts Hermes gateway after non-clean exit (e.g. exit 75) or wedged heartbeat. Script: $script"
# -Once triggers can get a finite repetition duration; clear it so the 5-min repeat runs forever.
$task.Triggers[0].Repetition.Duration = ''
$task | Set-ScheduledTask | Out-Null
