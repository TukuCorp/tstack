function Show-MorningBriefing {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "      Good Morning! Here's your day:    " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    # --- Get Unread Emails ---
    Write-Host "`n[Gmail] Fetching Unread Count..." -ForegroundColor Yellow
    try {
        # Fetch unread emails
        $unreadJsonStr = gws gmail users messages list --params '{"userId": "me", "q": "is:unread in:inbox"}'
        $unreadJson = $unreadJsonStr | ConvertFrom-Json
        
        $unreadCount = 0
        if ($unreadJson.messages) {
             if ($unreadJson.resultSizeEstimate) {
                 $unreadCount = $unreadJson.resultSizeEstimate
             } else {
                 $unreadCount = $unreadJson.messages.Length
             }
        }
        
        if ($unreadCount -eq 0) {
             Write-Host "  Inbox Zero! You have no unread emails." -ForegroundColor Green
        } else {
             Write-Host "  You have $unreadCount unread emails in your inbox." -ForegroundColor Red
        }
    } catch {
        Write-Host "  Failed to fetch email data." -ForegroundColor DarkGray
    }

    # --- Get Today's Calendar Events ---
    Write-Host "`n[Calendar] Today's Schedule:" -ForegroundColor Yellow
    try {
        # Get start and end of current day in ISO 8601 format compatible with Google Calendar API
        $todayStart = (Get-Date).Date.ToString("yyyy-MM-ddTHH:mm:ssK")
        $todayEnd = (Get-Date).Date.AddDays(1).AddSeconds(-1).ToString("yyyy-MM-ddTHH:mm:ssK")
        
        $eventsJsonStr = gws calendar events list --params "{`"calendarId`": `"primary`", `"timeMin`": `"$todayStart`", `"timeMax`": `"$todayEnd`", `"singleEvents`": true, `"orderBy`": `"startTime`", `"maxResults`": 10}"
        $eventsJson = $eventsJsonStr | ConvertFrom-Json
        
        if ($eventsJson.items -and $eventsJson.items.Length -gt 0) {
            foreach ($event in $eventsJson.items) {
                $summary = $event.summary
                
                if ($event.start.dateTime) {
                    # Convert to local time format
                    $startTime = [datetime]::Parse($event.start.dateTime).ToLocalTime().ToString("hh:mm tt")
                    Write-Host "  [$startTime] $summary" -ForegroundColor White
                } else {
                    # It's an all-day event
                    $summary = $event.summary
                    Write-Host "  [All Day] $summary" -ForegroundColor White
                }
            }
        } else {
            Write-Host "  Your calendar is clear today!" -ForegroundColor Green
        }
    } catch {
        Write-Host "  Failed to fetch calendar data." -ForegroundColor DarkGray
    }
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host ""
}

# Run it when profile loads
# Show-MorningBriefing

# Codex: opencodex proxy (opencode-go models) isn't a service; start it if nothing listens on 10100.
function codex {
    $tcp = New-Object Net.Sockets.TcpClient
    $up = try { $tcp.ConnectAsync('127.0.0.1', 10100).Wait(300) } catch { $false } finally { $tcp.Dispose() }
    if (-not $up) { ocx ensure *> $null }
    & "$env:LOCALAPPDATA\Programs\OpenAI\Codex\bin\codex.exe" @args
}

# Claude Code with experimental Code Mode for this session only (no Claude in Chrome / Remote Control while on).
function claude-code-mode {
    $env:CLAUDE_CODE_EXPERIMENTAL_CODE_MODE = '1'
    try { claude @args } finally { Remove-Item Env:CLAUDE_CODE_EXPERIMENTAL_CODE_MODE -ErrorAction SilentlyContinue }
}

# agy: YOLO by default (no settings key exists for --dangerously-skip-permissions as of agy 1.5.16).
# Subcommands (models, mcp, update...) pass through unchanged.
function agy {
    $exe = "$env:LOCALAPPDATA\agy\bin\agy.exe"
    $sub = 'acp','agent','agents','changelog','help','install','mcp','mic-serve','models','plugin','plugins','remote-control','update'
    if ($args.Count -gt 0 -and $sub -contains $args[0]) { & $exe @args }
    elseif ($args -contains '--dangerously-skip-permissions') { & $exe @args }
    else { & $exe --dangerously-skip-permissions @args }
}
