@echo off
setlocal enabledelayedexpansion
REM ===========================================================================
REM graphify_update.bat  --  TEMPLATE
REM
REM Manual, no-AI live-graph refresh + smoke test. Copy this into your
REM project's  tools\  folder and adjust CODE_DIR below to your source folder
REM (lib / src / app / internal ...). Run it after code changes or to check
REM graphify works.
REM
REM What it does (no LLM, no API key, no token cost):
REM   [1/2] Code-only AST refresh of the LIVE root graphify-out\graph.json via
REM         `graphify update`. GRAPHIFY_OUT is pointed at the root folder and
REM         CODE_DIR is passed absolute -- both required, otherwise the CLI
REM         writes a stray graph under CODE_DIR\graphify-out\ or re-anchors
REM         every node id. Directed flag + community labels are kept.
REM         Docs are not re-extracted; a FIRST build is the skill flow
REM              /graphify CODE_DIR --directed
REM         inside Claude -- never delete graph.json before running this bat.
REM   [2/2] Smoke test -- confirm the live root graph exists, is directed, and
REM         answers a query. This is the "does graphify actually work here" check.
REM ===========================================================================

REM ---- adjust this to your project's code folder -------------------------------
set "CODE_DIR=."
REM -----------------------------------------------------------------------------

REM This bat lives in tools\ ; run everything from the repo root so graphify
REM resolves the live graph at .\graphify-out\ (relative to cwd).
pushd "%~dp0.."
set "RESULT=0"

REM Resolve the graphify launcher: prefer PATH, else derive from the interpreter
REM the last build saved (graphify.exe sits next to that python.exe).
set "GRAPHIFY=graphify"
where graphify >nul 2>nul
if errorlevel 1 (
  if exist "graphify-out\.graphify_python" (
    for /f "usebackq delims=" %%A in ("graphify-out\.graphify_python") do set "GPY=%%A"
    set "GRAPHIFY=!GPY:python.exe=graphify.exe!"
  ) else (
    echo ERROR: graphify not on PATH and no graphify-out\.graphify_python found.
    echo Build the graph once in Claude:  /graphify %CODE_DIR% --directed
    popd & endlocal & exit /b 1
  )
)

echo === [1/2] live-graph AST refresh (no LLM) : %CODE_DIR% ===
set "GRAPHIFY_OUT=%CD%\graphify-out"
"%GRAPHIFY%" update --force "%CD%\%CODE_DIR%"
if errorlevel 1 if "!RESULT!"=="0" set "RESULT=!ERRORLEVEL!"
echo.

echo === [2/2] smoke test: live root graph ===
if not exist "graphify-out\graph.json" (
  echo ERROR: graphify-out\graph.json not found.
  echo Build it in Claude:  /graphify %CODE_DIR% --directed
  popd & endlocal & exit /b 1
)
REM Report directed flag + node count of the LIVE root graph (should be directed:True).
if exist "graphify-out\.graphify_python" (
  for /f "usebackq delims=" %%A in ("graphify-out\.graphify_python") do set "GPY2=%%A"
  "!GPY2!" -c "import json;d=json.load(open('graphify-out/graph.json',encoding='utf-8'));print('directed:',d.get('directed'),'  nodes:',len(d.get('nodes',[])))"
  if errorlevel 1 if "!RESULT!"=="0" set "RESULT=!ERRORLEVEL!"
)
echo.
echo --- god nodes (top 5) ---
"%GRAPHIFY%" god-nodes --top 5
if errorlevel 1 if "!RESULT!"=="0" set "RESULT=!ERRORLEVEL!"
echo.
echo --- sample query ---
"%GRAPHIFY%" query "What are the main modules and how do they connect?"
if errorlevel 1 if "!RESULT!"=="0" set "RESULT=!ERRORLEVEL!"

popd
endlocal & exit /b %RESULT%
