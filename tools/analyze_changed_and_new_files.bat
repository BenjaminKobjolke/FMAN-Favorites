@echo off
for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
call "%~dp0analyze_code.bat" "main.py" --path "%PROJECT_ROOT%" --only-changed --verbosity minimal --output "code_analysis_results" --rules "code_analysis_rules.json"
exit /b %ERRORLEVEL%
