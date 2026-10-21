#!/bin/sh
# Delegate one coding-rules check to an external CLI.
# usage: coding_rules_delegate.sh <codex|deepseek> <prompt-file> <log-file>
#
# The prompt lives in a file so no long text reaches the command line, and the
# backend flags / redirection stay in here. Installed by /coding-rules:codex on
# or /coding-rules:deepseek on -- do not edit in the project, it gets overwritten.
set -u

[ $# -eq 3 ] || { echo "usage: $0 <codex|deepseek> <prompt-file> <log-file>" >&2; exit 2; }
[ -f "$2" ] || { echo "prompt file not found: $2" >&2; exit 2; }

prompt=$(cat "$2")

case "$1" in
  codex)    codex exec --dangerously-bypass-approvals-and-sandbox "$prompt" > "$3" 2>&1 < /dev/null ;;
  deepseek) reasonix run --auto "$prompt" > "$3" 2>&1 < /dev/null ;;
  *) echo "unknown backend: $1 (expected codex or deepseek)" >&2; exit 2 ;;
esac
