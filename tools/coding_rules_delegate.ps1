# Delegate one coding-rules check to an external CLI.
# usage: coding_rules_delegate.ps1 <codex|deepseek> <prompt-file> <log-file>
#
# The prompt lives in a file so no long text reaches the command line, and the
# backend flags / redirection stay in here. Installed by /coding-rules:codex on
# or /coding-rules:deepseek on -- do not edit in the project, it gets overwritten.
param(
    [Parameter(Mandatory = $true)][ValidateSet('codex', 'deepseek')][string]$Backend,
    [Parameter(Mandatory = $true)][string]$PromptFile,
    [Parameter(Mandatory = $true)][string]$LogFile
)

$ErrorActionPreference = 'Continue'

if (-not (Test-Path -LiteralPath $PromptFile -PathType Leaf)) {
    Write-Error "prompt file not found: $PromptFile"
    exit 2
}

$prompt = Get-Content -LiteralPath $PromptFile -Raw -Encoding UTF8

if ($Backend -eq 'codex') {
    & codex exec --dangerously-bypass-approvals-and-sandbox $prompt *> $LogFile
}
else {
    & reasonix run --auto $prompt *> $LogFile
}

exit $LASTEXITCODE
