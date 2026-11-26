#Requires AutoHotkey v2.0
#SingleInstance Force
; Home: hide the Herdr app window if it is in front, otherwise bring it back.
; Only the window is minimized/restored; herdr-core keeps every terminal running. Started at login from the Startup folder.
; Replaced noctty-toggle.ahk on 2026-11-26 when the Herdr app replaced noctty + the Herdr TUI.

Home:: {
    ids := WinGetList("ahk_exe herdr-app.exe")
    id := 0
    for w in ids {  ; topmost first; skip untitled helper windows (popups, tooltips)
        if WinGetTitle("ahk_id " w) != "" {
            id := w
            break
        }
    }
    if !id {
        Log("no herdr-app window")
        return
    }
    ; A minimized window can stay "active" when nothing else takes focus, so check minimized too.
    if WinActive("ahk_id " id) && WinGetMinMax("ahk_id " id) != -1 {
        WinMinimize("ahk_id " id)
        Log("hide " id)
    } else {
        from := WinGetProcessNameSafe()
        if WinGetMinMax("ahk_id " id) = -1
            WinRestore("ahk_id " id)
        WinActivate("ahk_id " id)
        ok := WinWaitActive("ahk_id " id, , 1)
        Log("show " id " from=" from " ok=" (ok ? 1 : 0))
    }
}

WinGetProcessNameSafe() {
    try return WinGetProcessName("A")
    return "?"
}

Log(msg) {
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") " " msg "`n", A_ScriptDir "\herdr-toggle.log")
}
