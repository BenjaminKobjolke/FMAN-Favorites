@echo off
call "%~dp0analyze_code.bat" "ruff_fixer.py" --path "." --rules "code_analysis_rules.json"
exit /b %ERRORLEVEL%
