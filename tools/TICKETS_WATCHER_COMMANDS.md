# Version
2

<!-- Managed by `tickets-watcher --setup`. Replaced whole when the version above changes;
     edit the shipped template in the tickets-watcher repo, not this copy. -->

# Writing a batch file that works as a Tickets Watcher command

A `.bat` or `.cmd` under `tools/` can show up as a command button in the Tickets Watcher app —
either named in the watcher's `settings.json` under `commands`, or offered by the app's picker as
any runnable file. The run starts in the project root and the process exit code is the run's
result, so end with an explicit `exit /b <code>`.

## Never block on a human

- **No `pause`.** The watcher strips it, but any other caller (CI, another bat, an agent) hangs
  forever. A bat that must open on `set /p` or `choice` is rewritten so the question becomes an
  app prompt — see *Prompts* below.
- **No `start` without `/wait`.** The run would finish while the started work continues and its
  output is lost. Use `start /wait` if you must open a window.
- **No GUI window that waits for a click.** Nothing will click it.

## Prompts

- A `set /p` or `choice` **in the started `.bat` itself** becomes a question answerable from the
  phone app. Keep prompts in the top-level bat.
- A prompt in a **second bat reached through `call`** is not rewritten and blocks until the run
  times out. Pass answers to it as arguments instead of asking inside it.
- PowerShell `Read-Host`, `Get-Credential` and `PromptForChoice` are not supported.

## Child programs that ask for input

A child program keeps the run from hanging only if it says so itself:

- **Reads a line** (Python `input()`, Node readline): print `::tw-input-line::` on its own
  flushed line immediately before reading, and only when `TICKETS_WATCHER_COMMAND_RUN=1` is set,
  so a normal terminal run is unchanged.
- **Reads stdin until EOF** (`codex exec`, `claude -p` and similar agent CLIs): give it closed
  stdin — `<NUL` in a bat, `stdin=subprocess.DEVNULL` in Python — or it waits forever on the
  watcher's open pipe.

## Things that behave differently here

- `%~n0` / `%~nx0` see the temporary `.tw-run-*` copy name. `%~dp0` is safe.
- The run has a time limit (`commands.timeout_seconds`); time spent waiting for an answer does
  not count against it.

## Analysis commands after implementation

The watcher can run configured test and code-quality commands before its analysis agent. Set
`analysis_command_kinds` for commands whose kind is not clear from the script name. Test and
code-quality commands have separate command limits: `analysis_test_timeout_seconds` defaults
to 540 seconds and `analysis_code_quality_timeout_seconds` defaults to 300 seconds. Either
setting falls back to `analysis_command_timeout_seconds` when present. Limits are capped at
1800 seconds.

Every test command also needs a per-test timeout shorter than its command limit. For pytest,
set `timeout = 120` in `pyproject.toml` or another supported pytest config; for Flutter, use
`--timeout` or `test/flutter_test_config.dart`. Setup warns when a configured pytest or Flutter
test command has no per-test timeout.

When a complete test command uses more than half its limit, the watcher raises the saved test
limit for the next todo. Keep scripts printing output during long runs: a long silent stretch
can create one low-priority follow-up asking for progress output.
