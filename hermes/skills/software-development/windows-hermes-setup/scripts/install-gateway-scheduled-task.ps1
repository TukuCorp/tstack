$action = New-ScheduledTaskAction -Execute "C:\Users\$env:USERNAME\AppData\Local\hermes\gateway-service\Hermes_Gateway.cmd"
$trigger = New-ScheduledTaskTrigger -AtLogon -User "$env:USERNAME"
Register-ScheduledTask -TaskName "Hermes Gateway" -Action $action -Trigger $trigger -Force

# Verify
Get-ScheduledTask -TaskName "Hermes Gateway" | Format-List State, Actions, Triggers
