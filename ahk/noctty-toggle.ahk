#Requires AutoHotkey v2.0
#SingleInstance Force
; Home: hide the noctty window (live herdr session) if it is in front, otherwise bring it back.
; Only the window is minimized/restored; herdr keeps running. Started at login from the Startup folder.
; Targets visible main windows only (class noctty.win32.host), so hidden quick-terminal/tooltip windows are skipped.

Home:: {
    ids := WinGetList("ahk_class noctty.win32.host ahk_exe noctty.exe")
    if !ids.Length {
        Log("no noctty window")
        return
    }
    id := ids[1]  ; topmost = most recently used
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
    try FileAppend(FormatTime(, "yyyy-MM-dd HH:mm:ss") " " msg "`n", A_ScriptDir "\noctty-toggle.log")
}
