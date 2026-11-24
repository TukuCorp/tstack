export PATH="$PATH:/c/Users/<USER>/AppData/Local/Microsoft/WinGet/Packages/arndawg.tmux-windows_Microsoft.Winget.Source_8wekyb3d8bbwe"

# agy: YOLO by default (no settings key for --dangerously-skip-permissions as of agy 1.5.16)
agy() {
  local exe="$LOCALAPPDATA/agy/bin/agy.exe"
  case "$1" in
    acp|agent|agents|changelog|help|install|mcp|mic-serve|models|plugin|plugins|remote-control|update) "$exe" "$@" ;;
    *) case " $* " in *" --dangerously-skip-permissions "*) "$exe" "$@" ;; *) "$exe" --dangerously-skip-permissions "$@" ;; esac ;;
  esac
}
