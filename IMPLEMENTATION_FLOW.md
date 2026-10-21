<!-- Managed by /coding-rules:apply — do not edit rule blocks by hand -->
<!-- codex: enabled -->
<!-- deepseek: disabled -->

# Version
25

Increase this version number whenever this rule file changes.

# Implementation Flow (All Languages)

See `COMMON_RULES.md` for rules that apply to all languages.

Unlike the per-language `*_RULES.md` files, these rules are **language-independent** and
**always apply**. They are not subject to the "some rules may not apply to this project"
filtering — include them in every project's `CODING_RULES.md`.

These rules define the end-to-end workflow an AI agent must follow when planning and
implementing changes. Each step is an existing skill referenced by its slash name; run the
skill rather than reimplementing its behavior.

---

## Delegation backends (Codex / DeepSeek)

Some of the workflow steps below can be delegated to an external CLI instead
of being performed by the agent itself. Two backends are supported, and they
are **mutually exclusive** — at most one is enabled at a time:

- `<!-- codex: enabled -->` — delegate to Codex
- `<!-- deepseek: enabled -->` — delegate to DeepSeek
- Neither marker `enabled` (or no marker) — do NOT delegate; perform the same
  checks yourself via the listed fallback skills.

Never call the backend CLI directly. Both backends are invoked through one
wrapper script installed in the project by `/coding-rules:codex on` /
`/coding-rules:deepseek on`, from the repo root:

```
tools/coding_rules_delegate.sh <backend> <prompt-file> <log-file>
```

`<backend>` is `codex` or `deepseek`. The wrapper holds the backend flags, the
log redirection and the closed stdin — the agent never types them. That keeps
the command line short and boring, which is what stops Claude Code's permission
classifier from denying the call.

Use the Bash tool with the `.sh`. Only if the Bash tool is unavailable, use the
PowerShell tool with `tools/coding_rules_delegate.ps1` (same three arguments).
Type the command exactly as written above — the permission entry matches a
literal command prefix, so an absolute path or an extra `cmd` wrapper misses it.

Read precedence if both markers somehow end up `enabled`: Codex wins, then
DeepSeek, then the self-fallback.

**Self-fallback in a subagent.** When neither backend is enabled, prefer
running each fallback skill in a subagent (Agent/Task tool, `general-purpose`
type) rather than inline — the skill's file reads and reasoning stay out of
the main context window. The subagent runs the skill and returns **only**
its summary (and the list of files it changed). Any file edits the skill
makes (plan file, code) persist, so the main agent picks them up.

Exceptions that MUST stay in the main context: `/plan:dry-checked` (it
reloads the adjusted plan INTO context) and restating the
Definition-of-Done / DRY gate aloud.

**Graphify preamble (optional).** If this project's `CODING_RULES.md` includes
the graphify addon, prepend its graphify delegate preamble to every `<PROMPT>`
below before invoking the backend CLI (see the graphify addon's "Delegated
checks" section). If the addon is not present, send `<PROMPT>` unchanged.

The markers are managed by `/coding-rules:codex on|off|status|test` and
`/coding-rules:deepseek on|off|status|test` (or set during
`/coding-rules:apply`). Do not flip them yourself without the user asking.

### Delegation contract (never let a delegate hang)

Applies to EVERY delegated `<PROMPT>` below, both backends. A delegate that
stops to ask a question blocks forever on stdin nobody can answer — these four
rules make that impossible and leave a debug trail when it happens anyway.

- **Prompt file.** Never put `<PROMPT>` on the command line. Write it (the
  no-questions suffix and, if applicable, the graphify preamble included) with
  the Write tool to a file next to the plan, named
  `<plan-file-path-without-.md>-<step>-prompt.txt` where `<step>` is `plan-dry`,
  `convention` or `post-impl`. Pass that path as argument 2 of the wrapper.
  Overwrite it per run.

- **No questions.** Append this suffix to every `<PROMPT>` before sending it:

  > "Run fully non-interactively. NEVER ask a question and NEVER wait for
  > input. If anything is ambiguous, blocked, or you cannot complete the task,
  > do NOT stop to ask — write your questions and what blocked you into your
  > output file (the plan file, or the check file for steps that write one)
  > under a heading `## DELEGATE QUESTIONS`, then exit immediately. Always
  > write the required SUMMARY block, even on failure."

- **Foreground, with a timeout.** Run every delegate call in the FOREGROUND with
  `timeout: 600000` (10 min, the Bash tool maximum). Never make an untimed
  delegate call, and never pass `run_in_background: true` — not for the delegate
  itself and not for a loop that waits on it. Backgrounding means ending your turn
  to wait for the notification, and in a headless run (`claude -p`, an agent-driven
  session, a subagent) the turn ending kills the process and every background task
  with it: the delegate dies mid-check, its summary never arrives, and the session
  exits 0 having done nothing. Block on the call instead.

- **Log.** Argument 3 is a log next to the plan file, named
  `<plan-file-path-without-.md>-<step>-delegate.log` (same `<step>` values as
  the prompt file). The wrapper captures stdout+stderr there and closes stdin,
  so a delegate that ignores the contract dies instead of blocking:

  ```
  tools/coding_rules_delegate.sh codex "<prompt-file>" "<log>"
  ```

  The log is overwritten per run. On any failure, report the log path to the
  user in one line — that is the debug handle.

- **Success check.** A delegated step counts as done only if its required
  SUMMARY block is present (`SUMMARY DRY`, `SUMMARY CONVENTION CHECK`, or the
  post-implementation check file). A permission
  block/denial, timeout, non-zero exit, missing SUMMARY, or a
  `## DELEGATE QUESTIONS` heading all count as failure. Never retry a failed
  delegate call. How to handle the failure depends on its kind:

- **Permission failure — STOP and ask the user.** If a backend is enabled but
  the call never ran because it was blocked or denied (permission prompt
  denied, the permission classifier blocked it, or the error is an
  approval/permission error rather than backend output), do NOT run the
  `delegate disabled` branch, do NOT perform the check yourself, and do NOT
  perform any other action designated for the delegate. The same applies if the
  wrapper script itself is missing (`tools/coding_rules_delegate.sh` not found).
  Report in one line which command was blocked and the likely cause — the
  wrapper is not installed, or the permission entry
  `Bash(tools/coding_rules_delegate.sh:*)` /
  `PowerShell(tools/coding_rules_delegate.ps1:*)` is missing — then ASK the user
  how to proceed, offering:

  1. install the wrapper + permissions (`/coding-rules:codex on` /
     `/coding-rules:deepseek on`) and re-run the delegated step,
  2. run the `delegate disabled` fallback in a subagent this once,
  3. skip the step.

  Wait for the answer. The workflow stays paused — the DRY gate is NOT cleared,
  so implementing does not start.

- **Other failures — fallback.** For timeout, non-zero exit, missing SUMMARY,
  or `## DELEGATE QUESTIONS`: report one line plus the log path, then run that
  step's `delegate disabled` branch (subagent). If the delegate wrote
  `## DELEGATE QUESTIONS`, answer those questions yourself in the fallback run,
  or surface them to the user if they need a decision.

These rules apply to EVERY delegated step below — the plan DRY + convention
check and the post-implementation DRY audit. (The graphify refresh is a plain
CLI call, never delegated.)

## Feature / Change Workflow

After a plan is proposed and the user approves it, follow this chain. The DRY
gate is a precondition for implementing — not just an earlier step.

The approved plan must first exist as an explicit Markdown file. Pass that same
path to both plan-DRY commands.

```
plan approved

plan DRY + convention check — one step; conventions first, so what already
exists in the codebase informs the DRY rewrite instead of arriving after it
  delegate enabled (codex or deepseek — write <PROMPT> to the prompt file and run
  `tools/coding_rules_delegate.sh <backend> <prompt-file> <log>` with <step> = plan-dry,
  see Delegation backends above; prepend graphify preamble if applicable; obey the
  Delegation contract — prompt file, no-questions suffix, timeout, log, SUMMARY check;
  this step needs BOTH summary blocks, a missing one counts as a failed SUMMARY check):
    <PROMPT> = "FULL PATH TO PLAN $convention-check - First scan the codebase for the existing utilities, patterns and naming conventions this plan should reuse. Then, with those findings in hand, check the plan for DRY, KISS and YAGNI opportunities. Apply both sets of findings to the original plan file. Only edit the plan file — do NOT modify any source code or implement the plan. Always end with two summary blocks: SUMMARY CONVENTION CHECK — what you reused and why, or 'No convention issues found.' — and SUMMARY DRY — what you consolidated and why, or 'No DRY opportunities found.'"
  delegate disabled (two subagents, in this order — /convention:check is
  read-only and its report does not reach the /plan:dry subagent by itself):
    1. run /convention:check in a subagent (see "Self-fallback in a subagent")
    2. apply its findings to the plan file yourself
    3. run /plan:dry <plan-file> in a subagent; inline only if a subagent
       isn't available.

/plan:dry-checked    reload the DRY and convention adjusted plan

restate Definition-of-Done aloud

implement
  While implementing, keep the list of every file you created or modified in THIS
  session — you know it from your own edits; do NOT derive it from git (other
  sessions may have concurrent uncommitted changes). After implementing, write the
  list (one path per line) to a changed-files file next to the plan, named after it:
  <plan-file-path-without-.md>-changed-files.md
  (e.g. claude-plans/my-feature-changed-files.md). The plan file is unique per
  session, so concurrent sessions never collide.
  Include only source-code files. Exclude documentation and other non-code
  files (`.md`, plain-text docs, the plan file itself) — the DRY audit only
  looks at code.

post-implementation DRY audit — scope is ONLY the changed-files file above
  delegate enabled (codex or deepseek — write <PROMPT> to the prompt file and run
  `tools/coding_rules_delegate.sh <backend> <prompt-file> <log>` with <step> = post-impl,
  see Delegation backends above; prepend graphify preamble if applicable; obey the
  Delegation contract — prompt file, no-questions suffix, timeout, log, SUMMARY check):
    <PROMPT> = "Read FULL PATH TO CHANGED-FILES FILE and check ONLY the files listed there for DRY opportunities. Do not use git status or git diff to widen the scope — other sessions may have concurrent uncommitted changes. Do NOT modify any code. Write your suggestions to <plan-file-path-without-.md>-post-implementation-check.md (next to the plan, same naming as the changed-files file), overwriting the file if it already exists. Include for each finding the affected files and a short rationale. Always write the file, even if you found nothing — in that case write a SUMMARY block stating 'No DRY opportunities found.'"
    then read that post-implementation-check file, validate each finding, and apply the valid ones. Bring a finding to the user only if a question arises — otherwise apply silently.
  delegate disabled:
    run /dry:check <files from the changed-files file, as pathspec> in a
    subagent (see note)

Post-Feature Verification + Post-Implementation Code Analysis (project-specific, below)

refresh graphify graph — only if the graphify addon is present in this project's CODING_RULES.md
  A seconds-long, no-LLM CLI call. Run it YOURSELF via Bash from the repo root — no
  delegate, no subagent, no graphify skill load. <code-dir> is the scan root pinned in
  the project's CODING_RULES.md / CLAUDE.md (one call per dir for multi-path graphs):
    GRAPHIFY_OUT="$PWD/graphify-out" graphify update "$PWD/<code-dir>"
  Both halves are mandatory — the absolute GRAPHIFY_OUT keeps the write in the root
  graphify-out/ and the absolute <code-dir> keeps node ids stable (details in the
  graphify addon's "Refreshing after a code change" section, copied into CODING_RULES.md).
  Success = exit 0 ("No code-graph topology changes detected" is also success).
  Then verify, cheap: root graphify-out/graph.json has `directed: true`, the node count
  did not collapse, and no <code-dir>/graphify-out/graph.json appeared.
  On failure: report the decisive output line in one line. `refused to shrink` → re-run
  with `--force` only if this change really deleted source files. Missing or corrupt
  graphify-out/graph.json → do NOT run the CLI (it would rebuild undirected); run the
  full skill build `/graphify <code-dir> --directed` in a subagent (see "Self-fallback
  in a subagent") — never in the main context, the skill loads a large instruction file.
```

### Docs-only changes — skip the DRY and convention steps

Skip the `plan DRY + convention check`, `/plan:dry-checked` and the
post-implementation DRY audit when the plan changes **only** non-code files —
the same exclusion the changed-files file uses: `.md`, plain-text docs, pure
prose content, the plan file itself. A phase file that states "prose only — no
code changes in this phase" is the typical case.

Both checks exist to find code to reuse and code to consolidate. With no code in
scope they always return "No convention issues found." / "No DRY opportunities
found." — a delegate call and a 10-minute timeout for a known answer.

Instead say in one line that you are skipping them and why
(`Docs-only plan — DRY + convention check skipped`), then implement. Still
restate the Definition of Done; mark its DRY-gate and `/dry:check` boxes
`n/a — docs only`. `/verify:after-change` still runs.

Mixed code + docs, or unsure: run the checks. Not running them is the exception
and needs the file list to prove it.

### DRY gate (precondition for implementing)

Do not write a single line until ALL are true. Restate this gate aloud at the
moment you start implementing — if you cannot, the gate is not cleared:

- [ ] `/convention:check` found the existing utilities/patterns to reuse, and
      they are written into the plan file.
- [ ] `/plan:dry <plan-file>` adjusted that file and completed its Ponytail pass.
- [ ] `/plan:dry-checked <plan-file>` reloaded the same adjusted plan.

The gate survives the `implement` step: if mid-implementation you add a new
helper, type, or pattern the gate would have caught, stop and re-clear it
before continuing.

Docs-only plans clear the gate by exemption (see above) — but the survival rule
still applies in reverse: the moment a docs-only implementation touches a source
file, the exemption is void. Stop, run the check, then continue.

### Definition of Done — restate aloud before implementing

Before the first edit, state in chat what "done" means for THIS change:

- [ ] Scope: <one line — what changes, what does not>
- [ ] Reuse: <existing function/component this builds on, with path>
- [ ] DRY gate cleared (above)
- [ ] `/dry:check <session changed-files>` clean (scoped to the changed-files file, never bare; may run via subagent)
- [ ] `/verify:after-change` green (tests + analysis; may run via subagent)

### Post-implementation DRY audit — paste-in template

Run `/dry:check` scoped to the session's changed-files file, then paste and fill:

```
DRY audit — <change name>
Changed files:     <list from the changed-files file, not git>
Duplication found: <none | describe>
Consolidated into: <shared fn/module + path | n/a>
Convention reused: <name + path>
Verdict:           <clean | needs rework>
```

---

## Bug-Fix Workflow

Bug fixes use a shorter variant (no plan-DRY phase):

```
bugs:fix
  → /verify:after-change  (run in a subagent — see "Self-fallback in a
    subagent")
```

---

## Optional Addons

These live in `implementation_flow_addons/` and are **not** always-on. Each is opt-in per project — ASK
the user whether they want it before wiring it into that project's `CODING_RULES.md`.

- [`implementation_flow_addons/graphify.md`](implementation_flow_addons/graphify.md) — graphify knowledge graph:
  scoped + directed AST build, folder layout, gitignore, and the query rules. Lands in the
  project's `CODING_RULES.md`.
- [`implementation_flow_addons/graphify_flow.md`](implementation_flow_addons/graphify_flow.md) — the
  graphify steps that belong to the flow: the delegate preamble and the post-change refresh. Lands
  in the project's `IMPLEMENTATION_FLOW.md`. Opt into it together with `graphify.md`.

# Version
2

Increase this version number whenever this rule file changes.

# graphify Flow Steps (Optional Addon)

**Optional.** The flow half of the graphify addon — opt into it together with
`graphify.md`, which carries the folder layout and query rules and lands in the
project's `CODING_RULES.md`. These two sections land in the project's
`IMPLEMENTATION_FLOW.md` because they are steps of the implementation flow, not code
conventions: an orchestrator that runs the flow itself must be able to ignore them.

---

### Delegated checks (Codex / DeepSeek)

When this project delegates the plan/DRY/convention checks to an external CLI
(see `IMPLEMENTATION_FLOW.md` "Delegation backends"), prepend this **graphify delegate
preamble** to the `<PROMPT>` before sending it to that backend:

```
Graphify: this project has a graphify knowledge graph, built at the repo-root
`graphify-out/graph.json`. Run all graphify commands FROM THE REPO ROOT (the
graph is resolved relative to the current directory). For any codebase question,
run `graphify query "<question>"` first (also `graphify path "<A>" "<B>"`,
`graphify explain "<concept>"`) instead of raw grep.
```

Prepend only — do not otherwise change the `<PROMPT>`. The cwd line matters:
`codex exec` / `reasonix run` inherit the caller's directory, and `graphify
query` reads `graphify-out/` relative to cwd — run from a subdir and it finds
nothing, silently degrading to grep. Harmless if the graph is not built yet:
`graphify query` returns nothing and the CLI falls back to reading files.

### Refreshing after a code change

- After a feature or any code change, refresh the live graph with the **CLI update**, run
  from the repo root. One command, no LLM, no API key, seconds:
  ```
  GRAPHIFY_OUT="$PWD/graphify-out" graphify update "$PWD/<code-dir>"
  ```
  PowerShell: `$env:GRAPHIFY_OUT="$PWD\graphify-out"; graphify update "$PWD\<code-dir>"`.
  It re-extracts code files (AST, cached), re-clusters, keeps the existing community labels
  (signature-validated; a changed community is hub-named), preserves the semantic (doc)
  nodes of the last full build, and inherits `directed: true` from the existing graph
  (graphify ≥ 0.9.x, #2342). Prints `No code-graph topology changes detected` when the
  change was a no-op for the graph.
- **Both halves of the command are mandatory.** `graphify update` writes to
  `<path>/graphify-out/`, so without the absolute `GRAPHIFY_OUT` it creates a second,
  stray graph under `<code-dir>/graphify-out/` and the live root graph goes stale. And
  the `<code-dir>` must be **absolute**: with a relative path node ids and `source_file`
  get re-anchored to the repo root, every node is replaced and all labels are lost.
- **Never delete the root `graph.json` before a CLI update.** With no existing graph
  the CLI builds an **undirected** one (nothing to inherit) and the doc nodes are gone.
  Missing or corrupt `graph.json` → full skill rebuild (`/graphify <code-dir> --directed`,
  in a subagent — the skill loads a large instruction file).
- **Multi-path merged graphs** (`application/ framework/`): `update` takes one path — run
  the command once per scanned dir. The reconcile keeps nodes outside the watched subtree.
- **Rebuild at the scope the existing graph already has**, never narrower. Check
  `graphify-out/.graphify_root`; it stays the absolute `<code-dir>` after a CLI update
  (the CLI writes the path exactly as passed). Record the intended scan root in the
  project's `CLAUDE.md` — `.graphify_root` holds an absolute path and `graphify-out/` is
  gitignored, so it cannot carry the scope across clones.
- **Shrink guard.** A deleted source file is evicted normally. If the CLI still refuses
  with `refused to shrink`, the change really removed code — re-run with `--force`. Never
  force to paper over a wrong path or a wrong `GRAPHIFY_OUT`.
- **Doc changes** (`docs/`, `*.md`) are not re-extracted by the CLI (code only). Run the
  skill's incremental flow `/graphify <code-dir> --directed --update` occasionally for
  those; it costs LLM work. **Keep `docs/` in** the graph — it is the prose that answers
  "how does X work"; excluding it via `.graphifyignore` leaves a graph a grep would match.
- Verify after refresh (cheap, no skill load): root `graph.json` has `directed: true`,
  the node count did not collapse, and no `<code-dir>/graphify-out/graph.json` appeared.
  For a **multi-path merge**, also grep `graph.json` for a node-ID prefix belonging to a
  second scanned dir (e.g. `framework_`) to prove that dir is still in the graph.
