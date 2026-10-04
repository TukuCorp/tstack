@echo off
setlocal
set PYTHONPATH=
uv tool run --isolated %1 server --transport stdio %*
