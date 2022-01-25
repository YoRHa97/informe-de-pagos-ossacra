@echo off
%~d1
cd "%~p1"
start .venv/Scripts/python.exe app.py