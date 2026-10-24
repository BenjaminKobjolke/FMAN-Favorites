@echo off
if not exist "%~dp0analyze_code_config.bat" (
    echo ERROR: analyze_code_config.bat not found.
    echo Copy analyze_code_config.example.bat to analyze_code_config.bat and set your CLI_ANALYZER_PATH and LANGUAGE.
    exit /b 1
)
call "%~dp0analyze_code_config.bat"
if errorlevel 1 exit /b 1
if "%~1"=="" goto default_analyzer
set "ANALYZER_SCRIPT=%~1"
shift
set "ANALYZER_ARGUMENTS=%*"
goto launch_analyzer

:default_analyzer
set "ANALYZER_SCRIPT=main.py"
set "ANALYZER_ARGUMENTS=--path . --verbosity minimal --output code_analysis_results --maxamountoferrors 50 --rules code_analysis_rules.json"

:launch_analyzer
if /i "%ANALYZER_SCRIPT%"=="main.py" set "ANALYZER_ARGUMENTS=--language %LANGUAGE% %ANALYZER_ARGUMENTS%"
pushd "%~dp0.." || exit /b 1

"%CLI_ANALYZER_PATH%\venv\Scripts\python.exe" "%CLI_ANALYZER_PATH%\%ANALYZER_SCRIPT%" %ANALYZER_ARGUMENTS%
set "ANALYZER_EXIT_CODE=%ERRORLEVEL%"

popd
exit /b %ANALYZER_EXIT_CODE%
