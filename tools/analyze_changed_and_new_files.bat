@echo off
call "%~dp0analyze_code.bat" "main.py" --path "." --only-changed --verbosity minimal --output "code_analysis_results" --rules "code_analysis_rules.json"
exit /b %ERRORLEVEL%
