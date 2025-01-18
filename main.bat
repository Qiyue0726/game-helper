@echo off&(cd/d "%~dp0")&(cacls "%SystemDrive%\System Volume Information" >nul 2>&1)||(start "" mshta vbscript:CreateObject^("Shell.Application"^).ShellExecute^("%~snx0"," %*","","runas",1^)^(window.close^)&exit /b)
@echo off
cd "E:\Code\game-helper\"
python main.py
