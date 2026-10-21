<!-- Managed by /coding-rules:apply — do not edit rule blocks by hand -->

# Version
12

Increase this version number whenever this rule file changes.

# Common Rules (All Languages)

These rules apply to all projects, regardless of language. Language-specific rules live in the
corresponding `*_RULES.md` files.

---

## Keep CODING_RULES.md in Sync

When working on a project, copy all relevant rules into the project's `CODING_RULES.md` file
(project root). The project's `CLAUDE.md` carries only a small versioned pointer block that
mandates reading `CODING_RULES.md` before code work — never the full rules, and never an
`@import` of `CODING_RULES.md` (imports auto-expand into context every turn).

- Always include all rules from `COMMON_RULES.md` and `IMPLEMENTATION_FLOW.md`.
  `COMMON_RULES.md` is copied into the project's `CODING_RULES.md`;
  `IMPLEMENTATION_FLOW.md` is copied into the project's own `IMPLEMENTATION_FLOW.md`
- Also include applicable language-specific, project-type, and supplemental rule files
  (see `PROJECT_TYPES.md` for the project-type overview)
- Include optional addon rule files only when the user has opted in to that addon
- If applicability is unclear, ask the user which rules to include
- Include each source file's `# Version` block with its copied rules
- If `CODING_RULES.md` already exists, compare each source file's version with the corresponding
  copied rule block and update only stale or unversioned blocks, keeping the result deduplicated
- If `CLAUDE.md` contains inlined rule blocks or coding-rule `@import` lines from an earlier run,
  migrate that content into `CODING_RULES.md` and leave only the pointer block in `CLAUDE.md`

---

## Use Objects for Related Values

When multiple related values must be passed between classes or methods, bundle them into a
dedicated object (e.g., DTO/Settings/Config) instead of passing many parameters. This improves
readability, reduces call-site churn, and makes changes safer.

---

## No Bag-of-Keys Returns at Module Boundaries

When a public method on a manager/repository/service returns data that crosses a module
boundary, the return type must be a typed object (DTO, value object, or domain model) — never
a raw associative array indexed by string keys. Plain `array` returns silently swallow shape
bugs: a missing key reads as `null`, a list-vs-single mix-up reads as "no data", and renames
go undetected by static analysis.

- **Anti-pattern.** `getSettingsValue(...)` returns `array|null`; callers do `$result['value']`,
  `$result['type']`. A consumer mis-indexes `$result[0]['value']` after a refactor; nothing
  flags the change. The function silently returns `null` and downstream defaults take over.
- **Correct pattern.** Return a class — `getSettingsElement(...): ?SettingsElement`. The class
  exposes `getValue()`, `getType()`, `exists()`. Typed, autocompleted, statically checked;
  renames propagate via the IDE.
- **Lists vs single must be obvious from the type and the name.** `getThing(): ?Thing`
  (zero or one) vs `getThings(): ThingList` or `iterable<Thing>`. Never overload the same
  return type to mean both.
- **Distinguish absent from empty.** `null` from a lookup means "not found"; an empty
  collection means "found, but had nothing". A typed return makes this contract explicit;
  a bag-of-keys array hides it.
- **JSON-decoded blobs are arrays too.** The rule applies equally to `json_decode($column, true)`
  results that cross a module boundary — wrap them in a value object before they leave the
  layer that owns the schema.
- **Internal helpers may stay arrays.** This rule targets *public* API on managers and the
  boundary where a domain abstraction starts. Pure-private array juggling inside a single
  method is fine.

---

## Reuse Existing Models Before Inventing Array Shapes

Before designing a new return type or DTO, search the codebase for an existing domain class
that already owns the same data. Most "should this be a DTO?" decisions are actually
"is there already a `Contest` / `User` / `Order` class that should absorb this method?"

- Grep for the table name, the primary key, and the most distinctive column.
- If a model already exists with a constructor that accepts the row shape, use it — don't
  invent a parallel array shape that mirrors the same columns.
- Adding a `getXxxObject()` alongside a legacy `getXxxData()` is acceptable as a migration
  step; keep both only until consumers are migrated, then delete the array-returning version.

---

## Tests Pin the Shape Before the Refactor

When converting a bag-of-keys return to a typed object, write a **characterization test
first** that locks the current behavior using the existing API, run it green against the
unrefactored code, and then refactor. The same test (or a renamed-but-equivalent one) must
remain green afterward.

This converts "I think the new object preserves behavior" into "the test proves it." Pair
with the "Test-Driven Development" rule below — characterization tests are TDD applied to
refactors instead of new features.

---

## Test-Driven Development for Features and Bug Fixes

Follow TDD when implementing features or fixing bugs:

1. Write tests first
2. Run the tests and confirm they fail
3. Implement the change or fix
4. Run the tests again and confirm they pass

---

## Integration Tests

Every project must include integration tests in addition to unit tests. Integration tests verify that
components work correctly together and catch issues that unit tests alone cannot detect.

---

## Test Runner Scripts

Every project must provide the following batch files in the `tools/` directory:

- `tools/run_tests.bat` — runs unit tests
- `tools/run_integration_tests.bat` — runs integration tests

These scripts ensure a consistent way to execute tests across environments.

Both scripts must show progress while tests run: report the current setup stage, suite, or test
before potentially slow work, and show results as execution proceeds. A start banner followed only
by a final summary is insufficient. Prefer the runner's verbose output and stream or flush it so
callers can see it during execution. Print one line per test: `flutter test --reporter expanded`,
`pytest -v`, `phpunit --debug` (`--testdox` lists the tests only after the run on PHPUnit 10+).
For a legitimate long wait without ordinary output, report the current stage or test and elapsed
time at least every 60 seconds. Elapsed-time updates must not imply that a test completed or
advanced. If output is captured for logs or filtering, keep progress visible during execution;
replaying it only after completion does not count.

Both must **exit with the test runner's own exit code** — capture it right after the run
(`set TESTRESULT=%ERRORLEVEL%`) and end with `exit /b %TESTRESULT%`. A bat that prints
"Some tests failed!" but exits 0 reports green to CI, to callers and to AI agents. Never pipe the
test command into a plain filter — the pipe's exit code is the *filter's*, not the runner's. Never
redirect the run into a temp file and print or filter that afterwards either: the script is then
silent for the whole run. Run the command directly so its output streams. If output has to be
filtered or logged, do it while it streams and return the runner's own code, e.g. `powershell
-NoProfile -Command "<test command> | Where-Object { $_ -notmatch '<noise>' }; exit $LASTEXITCODE"`,
or use the runner's own log-file option.

---

## No `pause` in Batch Files

Batch files must never contain a `pause` line. `pause` waits for a keypress, so any bat that has one
hangs forever when run by CI, another bat, or an AI agent. End with an explicit `exit /b <code>`
instead, and let the caller decide whether to keep the window open (`cmd /k`).

---

## Prefer Type-Safe Values

Use strong, explicit types instead of loosely typed or stringly typed values (e.g., typed DTOs,
enums, generics, typed settings). This ensures mistakes are caught at compile time or by tests
early in development.

---

## String Constants

Centralize string constants in a dedicated module/class. Do not scatter raw strings across
the codebase. Use language-appropriate patterns for constants and reuse them consistently.

---

## Reusable Tooling

Before building project-specific infrastructure scripts (audits, codemods,
build helpers, lint checks, etc.) for a project, check the matching
language's `*_setup_files/` folder under this `coding-rules` repo for an
existing equivalent. If found, copy or reference it. If not:

1. Build the script in the project and prove it on real data.
2. Copy the script into the right `*_setup_files/tools/` folder.
3. Document it in that language's `*_RULES.md` so the next project picks
   it up automatically.

This keeps cross-project tooling consistent and prevents the same script
from being re-invented in every new project.

---

## New Projects Start From a Template

Before creating a new project (an API, an app, a tool — anything that gets its own folder),
ask the user whether a template project exists for that kind of project. Never scaffold from
scratch without asking.

- Run `/coding-rules:new-project`: it suggests the template remembered for that project type
  in `~/.coding-rules/settings.json`, asks, and remembers a newly chosen template for next time.
- A remembered template is a suggestion — still ask, the user may want another one or none.

---

## README.md is Mandatory

Every project must have a `README.md` file in the root directory. It should include:

- Project name and description
- Installation/setup instructions
- Usage examples
- Dependencies and requirements

---

## Don't Repeat Yourself (DRY)

Avoid code duplication. If the same logic appears in multiple places, extract it into a
reusable function, class, module, or utility.

- Duplicate code is harder to maintain and leads to bugs
- Extract shared logic into helpers or base abstractions
- Use constants for repeated values

---

## Derive, Don't Duplicate — One Value Owns the Derivation

When one value strictly determines another, pass only the determinant and derive the rest —
never thread both side-by-side through call sites, constructors, and events. Two co-varying
parameters are a functional dependency in disguise; passing both lets them drift into illegal
combinations.

- **Anti-pattern.** `createLog(ActionCategory $cat, ActionType $type)` threaded through ~10
  sites. Nothing stops a caller passing `category: email, type: lead.created`.
- **Correct pattern.** The richer type owns the relationship: `ActionType::category()` returns
  its `ActionCategory` via a single exhaustive `match`. Call sites pass only `ActionType`;
  category is always derived, so a mismatch is unconstructable.
- **Apply when** one value *determines* the other (a true functional dependency).
- **Don't apply when** the relationship is many-to-many or genuinely independent — forcing a
  derivation that doesn't exist couples things that should stay separate.
- **Keep derivation cheap and pure** — a getter/match, no DB or IO behind a call that looks free.
- **Keep the mapping exhaustive** (enum + exhaustive match) so a new case cannot silently skip
  its derived value.

This is Single Source of Truth applied to parameters, and a form of "make illegal states
unrepresentable." Pairs with "Prefer Type-Safe Values" and "Self-Describing Classes".

---

## Keep It Simple (KISS)

Prefer the simplest solution that actually works. Complicated logic for a simple result must be
kept to a minimum — a future maintainer (or you, at 3am) has to understand it.

- **YAGNI.** Don't build for a need that isn't here yet: no interface with a single
  implementation, no factory for one product, no config for a value that never changes.
- **Boring over clever.** Clever is what someone decodes later. The obvious solution wins.
- **Deletion over addition.** The shortest working change is usually the right one.
- Pairs with "Don't Repeat Yourself" and "No God Classes" — simplicity is what those rules
  are protecting.

---

## Confirm Dependency Versions

Before adding any new package or library, confirm the version with the user to ensure we use
up-to-date dependencies.

- Do not assume which version to use
- Ask the user to verify the latest stable version
- Avoid outdated packages that may have security vulnerabilities or missing features

---

## Error Handling & Logging Strategy

Every project must have a centralized error handler rather than ad-hoc try/catch blocks scattered
throughout the codebase.

- Use structured logging (not `print`/`console.log`/`echo`)
- Log at appropriate levels: debug, info, warning, error
- Include context in log messages (module name, operation, relevant IDs)

---

## Centralized Logger — Single Off Switch

Route all logging through one dedicated logger class/module. Never call the language's
built-in output directly for logging (`print`, `console.log`, `echo`, `Debug.Log`,
`System.out`). Code calls the project logger; the project logger wraps the underlying sink.

- **One toggle.** Because every log goes through one place, logging can be turned off,
  level-filtered, or redirected (file, console, remote) from a single config flag — without
  touching call sites. Example: a `logEnabled` / `logLevel` setting the logger checks once.
- **Levels live in the logger.** Callers pass a level (debug/info/warning/error); the logger
  decides what is emitted based on central config. Callers never branch on "should I log?".
- **Wrap, don't scatter.** Built-in calls (`print`, framework loggers, `Debug.Log`) appear
  in exactly one file — the logger implementation. Everywhere else imports the logger.
- **Language specifics** still apply (e.g. Unity `[Conditional]` stripping, Flutter `logger`
  package, Python `logging`) — but they are configured inside the central logger, not at
  call sites.

The logger's name is fixed per language so it is the same known type in every project (see each
`*_RULES.md` for details):

| Language      | Class / export     | File                |
|---------------|--------------------|---------------------|
| Python        | `AppLogger`        | `app_logger.py`     |
| PHP           | `Logger`           | `Logger.php`        |
| Dart/Flutter  | `AppLogger`        | `app_logger.dart`   |
| Kotlin        | `AppLogger`        | `AppLogger.kt`      |
| C# (plain)    | `AppLogger`        | `AppLogger.cs`      |
| Unity C#      | `GameLog` (static) | `GameLog.cs`        |
| Svelte/JS/TS  | `logger` (export)  | `logger.ts`         |
| Arduino       | `Log`              | `Log.h` / `Log.cpp` |

---

## Input Validation at Boundaries

Always validate data at system boundaries — API inputs, user input, file uploads, external service
responses.

- Never trust external data; validate before processing
- Use language-appropriate validation libraries (e.g., Pydantic, Zod, FluentValidation)
- Fail fast with clear error messages when validation fails

---

## API Clients: the API Sorts, Filters and Pages (BINDING)

Applies to every project that reads data from an API — app, SPA, desktop tool, script.

- **Show what the API returns, in the order it returns it.** Never download a whole collection
  to sort, filter, search, count, group or join it locally.
- **Read lists page by page.** Send the page size and position and load the next page when the
  user scrolls or asks for more. Never loop over all pages to rebuild the full list on start or
  on refresh.
- **A new order, filter or search is a new request** with that parameter, starting at the first
  page. Reordering the rows already held is wrong as soon as the list is paged: the client holds
  one page, not the list.
- **Do not download again what you already hold.** After a create, update or delete use the row
  the response returned, or re-request the visible page — not the whole collection.
- **A missing parameter is API work.** When an API you own lacks the sort, filter, search,
  paging or count a screen needs, request it from the API project (linked todo or
  `/feedback:write`) and plan against that. "The list is small or unpaged today, so the client
  can do it" is not a reason. For a third-party API that cannot change, use the paging and
  sorting it offers and mark any remaining local work with a comment naming the missing
  capability.

The server half is `project_type/REST_API.md` -> "List Endpoints: Paging, Sorting, Filtering".

---

## Shared Contract Repository for API and Clients (BINDING)

When two or more projects we own talk over the wire — an API plus an app, an API plus a desktop
app, or all three — keep their shared values in one contract repository. This does not apply to
third-party APIs.

- **Why:** each side keeps its own copy of every value that crosses the wire. When one side adds a
  value the other does not know, the other side can break (for example, the API added a todo type
  and the watcher rejected the whole todo list).
- **One separate repository** (`<system>-contract`) holds the contract: at minimum every shared
  enum in `enums.json`, shaped as `"<Name>": {"values": [sorted unique], "direction":
  "api_to_client" | "client_to_api", "description": "<where it appears>"}`, plus a `README.md`
  with the change rules and the list of consumers. Do not add version numbers; the submodule
  pointer is the version.
- **Every project includes it as a git submodule at `contract/`.** Pick up changes with
  `git submodule update --remote contract` and commit the pointer bump. Production code never
  reads `contract/`; it is test input only.
- **The API is the producer:** export the contract from its own constants (one map, one export
  script) and add a freshness test that fails when the committed file differs from the export.
- **Each client is a consumer:** test that every mapped enum matches the contract in its
  direction (`api_to_client` sets are equal so the client knows every value;
  `client_to_api` client values are a subset) and that every contract name is mapped.
- Both tests skip when `contract/` is not checked out.
- **Change order:** for an `api_to_client` value, update the contract, release clients that know
  it, then have the API emit it. For a `client_to_api` value, update the contract and API first,
  then have the client send it. To remove a value, stop it at the API, then remove it from the
  contract, then from clients. Never rename a value; renaming is an add plus a remove. Add a new
  shared enum to the contract in the same change that introduces it.
- Clients still tolerate an unknown value (skip the row; do not fail the whole response) as a
  last line of defence, not as permission to skip the order.
- **Setting it up** is work in each project: when one project of the system lacks the submodule
  or its test, request it there (linked todo or `/feedback:write`).

---

## Maximum File Length — 300 Lines

Split files when they exceed 300 lines to keep code navigable during fast iteration.

- Extract classes, functions, or components into separate modules
- Group related extractions logically (by domain, not by type)
- Exceptions: generated files, configuration files, test files with many similar cases

---

## Naming Conventions

Be consistent within a project. Follow these defaults unless the language or framework dictates
otherwise:

- Files: `snake_case` (or language convention, e.g., `PascalCase` for C# classes)
- Classes: `PascalCase`
- Functions/methods: language convention (`snake_case` for Python/PHP, `camelCase` for Dart/JS/C#)
- Constants: `UPPER_SNAKE_CASE`
- Variables: language convention (`snake_case` for Python/PHP, `camelCase` for Dart/JS/C#)

---

## Comments Explain Why, Not What

Comment intent and non-obvious reasoning — not a restatement of the code. Good names carry the
*what*; comments carry the *why*.

- **Anti-pattern.** `i++ // increment i`. Redundant comments add noise and rot the moment the
  code changes.
- **Correct pattern.** Document *why* a workaround exists, why a non-obvious algorithm was
  chosen, or a constraint that isn't visible locally (`// API rejects batches > 500`).
- Prefer self-documenting code (clear names, small functions) over a comment that compensates
  for unclear code — see "Naming Conventions" and "Keep It Simple".
- Document the purpose of each module/class at its top.
- Keep comments in sync with the code; delete stale ones rather than letting them mislead.

---

## Security Baseline

Every project must follow these minimum security practices:

- Never commit secrets (`.env`, API keys, credentials, private keys)
- Escape output to prevent XSS/injection attacks
- Use parameterized queries or ORM-provided methods — never concatenate user input into queries
- Validate and sanitize all user input at system boundaries
- Keep dependencies updated to avoid known vulnerabilities

---

## No Hardcoded Environment Values

Never hardcode environment-specific values in code — filesystem paths, hostnames, IP addresses,
ports, base URLs. They differ across machines and environments and make code non-portable.

- **Anti-pattern.** `connect("192.168.1.50:5432")`, `open("C:\\Users\\bob\\data\\out.json")`.
- **Correct pattern.** Read them from the project's central config (the config class each
  `*_RULES.md` already mandates), with a committed `.example` template documenting every key.
- Distinct from the secrets rule above: this is about **portability** (runs anywhere), not
  secrecy. A non-secret hostname still belongs in config, not in code.

---

## No God Classes

A class that handles too many responsibilities becomes fragile, hard to test, and impossible to
reuse. Keep each class focused on a single purpose.

- **Warning signs**: more than 5 public methods, more than 4 constructor dependencies, or methods that span unrelated domains (e.g., a class that validates input, queries the database, and sends emails)
- Split by responsibility: extract collaborators (e.g., a `Validator`, a `Repository`, a `Notifier`) rather than piling logic into one class
- If you struggle to name the class without using "Manager", "Handler", "Service", or "Helper" as a catch-all, it likely does too much
- This complements the 300-line file rule — a short class can still be a god class if it owns too many concerns

---

## Self-Describing Classes

When behavior depends on which fields or properties a class has — such as search, serialization,
display, validation, or auditing — the class itself must declare those fields through a contract
(interface, abstract method, attribute/annotation, or introspection pattern). Never hardcode field
lists in consuming code.

- **Anti-pattern**: A search service contains a hardcoded list of fields to index for each entity;
  adding a new field requires updating every consumer manually
- **Correct pattern**: Each class implements a contract (e.g., `GetSearchableFields()`,
  `GetDisplayColumns()`) that returns its own relevant fields, so adding a field in one place
  automatically propagates everywhere
- This applies to any cross-cutting concern that operates over class fields: search, filtering,
  export, form generation, diffing, logging, etc.
- Combine with compile-time checks where the language supports them (e.g., sealed interfaces,
  exhaustive matching) to ensure new fields cannot be silently ignored

---

## Search Across Partial Words

When implementing user-facing search, split the query on whitespace and match every term as a
case-insensitive substring of the searchable text, regardless of term order. For example,
`release bat` should find `release_build.bat`. Preserve the project's existing searchable fields.

---

## Inject Collaborators, Don't Fold Dependencies In

Composition reuse comes in two shapes, and they differ sharply in how much coupling they add to
the reusing class. **Folding** a helper into a class (mixin, trait, multiple inheritance, copy-in
include) merges *all of the helper's own dependencies* into that class — reuse five such helpers
and every one of their imports is now the host's coupling. **Injecting** a collaborator adds a
single dependency: the collaborator, which is built once and shared as a hub.

Prefer injected collaborators. Reserve fold-in reuse for helpers that are stateless and carry no
dependencies of their own.

- **Anti-pattern**: A controller reuses five behavior mixins/traits; each brings its own service,
  DTO, and constant imports, so the controller transitively depends on a few dozen things and is
  hard to test in isolation.
- **Correct pattern**: Extract that behavior into a collaborator object injected via the
  constructor. The controller depends on the collaborator; the collaborator is reused across many
  controllers as a shared, well-tested hub.

### Inject services; never instantiate one inside a method

Constructing a service with `new` (or the language equivalent) inside a method hides the
dependency from the class's public contract and makes it impossible to substitute in a test. Pass
collaborators in through the constructor.

- **Anti-pattern**: A method does `helper = new EmailPreparer(); helper.prepare(...)`. Nothing in
  the class signature reveals the dependency, and no test can replace it.
- **Correct pattern**: Inject `EmailPreparer` once; the method calls the injected instance.

### Collapse config-callback swarms into one value object

When a base class pulls its configuration from the subclass through many small overridable getters
that the subclass fills in one-line-each, each getter is a separate touch-point and the wiring is
spread across dozens of methods. Bundle the related values into a single config object built once
and handed to the base (see **Use Objects for Related Values**). This also keeps such classes off
the wrong side of **No God Classes**.

- **Anti-pattern**: A subclass implements `getSendEndpoint()`, `getSendSuccessKey()`,
  `getSendFailureRedirect()`, and a dozen more one-line getters, each naming one constant.
- **Correct pattern**: The subclass builds one `SendConfig` value object once; the base reads its
  fields.

# Version
8

Increase this version number whenever this rule file changes.

# Python Rules (uv)

See `COMMON_RULES.md` for rules that apply to all languages.

## Optional rule files

- `python/WEB_TEMPLATES.md` — web templates with Jinja2 or Flask.
- `python/GUI.md` — PySide6 desktop interface.
- `python/LOCALIZATION.md` — translated content.
- `python/RELEASE.md` — release tooling.
- `python/INSTALLER.md` — Windows installer.
- `python/DATABASE.md` — SQLAlchemy database.

Run `/coding-rules:apply` to add one when the project gains it.

## Recipes

Ready-made implementations for recurring features. They are **not** copied into the
project — they live in the `coding-rules` plugin under `rules/python/recipes/`. Read the
matching recipe in full before implementing the feature, and follow it instead of
inventing a new approach.

- `python/recipes/SINGLE_INSTANCE.md` — prevent a second instance of the app from starting.

## CLI Menus

For **interactive command-line** applications, never hand-roll a menu out of `input()`
and printed option lists. Use **`pick`** — an arrow-key menu with a selection
indicator, scrolling for long lists, and optional multiselect — on its **blessed**
backend:

```bash
uv add "pick[blessed]"
```

**Always pass `backend="blessed"`.** `pick`'s default curses backend breaks on Windows
the moment the program runs a child that inherits the console — a `git` call, a build
step, anything streaming its output live. From then on curses stops translating the
arrow keys for the rest of the process: the keys still arrive, but as raw `ESC [ A`
sequences that `pick` ignores, so every later menu draws and then accepts nothing. It
looks like a hang and it is sticky — re-initialising curses does not recover it, and
neither does restoring the console mode. Only never letting the child touch the console
(capturing its output, which costs live streaming) or decoding the sequences avoids it.
blessed decodes them, so subprocesses keep the console and their live output.

### Wrap it — one menu helper per project

Never import `pick` at more than one call site. Wrap it in a single helper class
(e.g. `menu.py` / `UserChoicesHandler`) so keyboard handling, the indicator style,
and Ctrl-C behavior are defined once:

```py
# src/<pkg>/menu.py
import sys
from pick import pick


def show_menu(
    options: list[str],
    title: str,
    indicator: str = "*",
    default_index: int = 0,
) -> int:
    """Show an arrow-key menu; return the selected index. Ctrl-C exits."""
    try:
        _, index = pick(
            options=options,
            title=title,
            indicator=indicator,
            default_index=default_index,
            backend="blessed",  # never the curses default: see above
        )
        return index
    except KeyboardInterrupt:
        sys.exit(1)
```

### Keep option labels and actions in step

The menu returns an **index**, not a parsed letter. Build the label list and a parallel
list of typed action values (enum members — see "Prefer Type-Safe Values") in the same
place, so an option can never be shown without a handler:

```py
options: list[str] = []
actions: list[MenuAction] = []
options.append("Commit"); actions.append(MenuAction.COMMIT)
if repo.has_untracked:
    options.append("Add all"); actions.append(MenuAction.ADD_ALL)
options.append("Cancel"); actions.append(MenuAction.CANCEL)

action = actions[show_menu(options, title)]
```

### Testing

`pick` needs a real terminal, so tests must not call it. Patch the project's wrapper
(`show_menu`) — not `pick` itself — and assert on the option labels it was handed:

```py
monkeypatch.setattr("<pkg>.menu.show_menu", lambda options, title, **kw: 0)
```

Keep a non-interactive path for every menu (a CLI flag, or auto-select when there is a
single option) so the program stays scriptable and testable without a TTY. Have the
wrapper refuse outright when `sys.stdin`/`sys.stdout` is not a TTY: without a console the
menu blocks on a key that can never arrive, which reads as a freeze rather than an error.

Because the tests patch the wrapper, nothing in the suite ever drives a real menu — so
also keep a small manual script (`tools/menu_smoke.py` + a `.bat`) that opens a menu, runs
a subprocess inheriting the console, then opens another menu. That second menu is exactly
what the curses backend breaks, and only a human at a terminal can see it.

---

## Project Setup Scripts

Copy the setup batch files from the `python_setup_files/` folder bundled with the
coding-rules plugin (next to this rules file).

### install.bat

Initial project setup:

- Checks if `uv` is installed
- Creates virtual environment via `uv sync --all-extras`
- Runs tests to verify setup

### update.bat

Update all dependencies:

- Updates lock file with `uv lock --upgrade`
- Syncs updated dependencies
- Runs linting checks (`ruff`, `mypy`)
- Runs tests to verify compatibility

### tools/run_tests.bat

Run the test suite:

- Runs `pytest tests/ -v` with verbose output
- Shows pass/fail summary
- Projects that split unit/integration point it at `tests/unit`

### tools/run_integration_tests.bat

Run the integration test suite:

- Runs `pytest tests/integration -v`
- Same uv check + summary as run_tests.bat

### Usage

```bash
# First time setup
install.bat

# Run tests
tools\run_tests.bat

# Update dependencies
update.bat
```

---

# Essential Additional Rules (must-have)

## 1) Use `pyproject.toml` as the single source of truth

No scattered config files. Keep tooling config in `pyproject.toml` (and commit `uv.lock`).

Recommended baseline:

* Python version pinned (e.g. `>=3.11,<3.13`)
* Dependencies managed via `uv add ...`
* Lockfile committed: `uv.lock`

---

## 2) Enforce formatting + linting + type checking in CI

Minimum toolchain:

```bash
uv add --dev ruff mypy
```

Rules:

* Ruff handles lint + formatting (replace black/isort/flake8).
* MyPy (or pyright) for typing.
* CI must run: `ruff check`, `ruff format --check`, `mypy`.

---

## 3) Require type hints on public APIs

Rule of thumb:

* All public functions/classes/methods: typed parameters + return types.
* Use `typing` well: `Sequence`, `Mapping`, `Protocol`, `TypedDict`, `Literal` when helpful.
* Avoid `Any` unless you have a boundary (I/O, third-party libs).

---

## 4) Centralize configuration with environment-driven settings

No “magic values” in code. Use a single settings module with env overrides.

```py
# app/config/settings.py
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    env: str = os.getenv("APP_ENV", "dev")
    debug: bool = os.getenv("DEBUG", "0") == "1"
    default_lang: str = os.getenv("DEFAULT_LANG", "en")
```

Everything reads from `Settings`, not directly from `os.getenv()` scattered around.

---

## 5) Tests are mandatory, fast, and isolated

Use pytest:

```bash
uv add --dev pytest
```

Rules:

* Unit tests for core logic.
* No network in unit tests.
* Use tmp dirs / fixtures; no reliance on developer machine state.
* Run tests in CI on every push.

---

## 6) Use `spec=` with MagicMock to catch interface mismatches

`MagicMock` without `spec` accepts **any** attribute, even non-existent ones:

```python
# BAD - No interface validation
mock = MagicMock()
mock.nonexistent_attribute = "test"  # Silently works
mock.typo_method()                   # Also works - won't catch bugs!
```

**Always use `spec=ClassName`** to validate against the real interface:

```python
# GOOD - Validates against real class
from unittest.mock import MagicMock
from mylib import EmailMessage

mock = MagicMock(spec=EmailMessage)
mock.nonexistent = "test"  # AttributeError - catches the bug!
```

### Common Pitfall: Mocking Methods vs Attributes

If the real class has a **method**, mock it as a method:

```python
# Real class has: def get_body(self) -> str
class EmailMessage:
    def get_body(self) -> str:
        return "content"

# WRONG - Creates fake attribute that doesn't exist
mock = MagicMock()
mock.body = "test"  # EmailMessage has no .body attribute!

# CORRECT - Mock the actual method
mock = MagicMock(spec=EmailMessage)
mock.get_body.return_value = "test"
```

### Quick Reference

```python
from unittest.mock import MagicMock, patch

# Mock with spec (recommended)
mock_obj = MagicMock(spec=RealClass)

# Mock method return value
mock_obj.method_name.return_value = "value"

# Mock method to raise exception
mock_obj.method_name.side_effect = ValueError("error")

# Mock property (use PropertyMock)
from unittest.mock import PropertyMock
type(mock_obj).prop_name = PropertyMock(return_value="value")

# Patch with spec
with patch("module.ClassName", spec=RealClass) as mock_cls:
    mock_cls.return_value.method.return_value = "value"
```

---

## 7) Required Batch Files

Every project must include these batch files:

* `start.bat` - In the root directory, starts the application
* `tools/run_tests.bat` - Runs the test suite

---

## Async Patterns

Use `asyncio` for I/O-bound tasks (network requests, file I/O, database queries). Avoid blocking
calls (`time.sleep`, synchronous HTTP) in async contexts — they block the entire event loop.

---

## Validation

Use Pydantic for request and data validation at API boundaries. Define models for incoming data
and let Pydantic handle type coercion and error reporting.

---

## Structured Logging

Use `structlog` or the `logging` module with JSON formatters — not `print()`. Configure a
centralized logging setup that all modules use consistently.

Route all logging through one class named **`AppLogger`** (`app_logger.py`) that wraps
`structlog`/`logging`. Feature code calls `AppLogger`, never `logging.getLogger(...)` or
`print()` directly — this gives a single enable/level toggle without touching call sites.

---

## Self-Describing Classes

Implement the common "Self-Describing Classes" rule using a Protocol/ABC or dataclass field
metadata.

### Option A: Protocol with abstract method

```python
from typing import Protocol


class Searchable(Protocol):
    def get_searchable_fields(self) -> list[str]: ...


class Customer:
    def __init__(self, name: str, email: str, phone: str) -> None:
        self.name = name
        self.email = email
        self.phone = phone

    def get_searchable_fields(self) -> list[str]:
        return [self.name, self.email, self.phone]
```

### Option B: Dataclass field metadata

```python
from dataclasses import dataclass, field, fields

SEARCHABLE = "searchable"


@dataclass
class Customer:
    name: str = field(metadata={SEARCHABLE: True})
    email: str = field(metadata={SEARCHABLE: True})
    internal_notes: str = field(default="", metadata={SEARCHABLE: False})


def get_searchable_values(obj: object) -> list[str]:
    return [getattr(obj, f.name) for f in fields(obj) if f.metadata.get(SEARCHABLE)]
```

Prefer the Protocol approach for simple cases. Use dataclass metadata when you need declarative
per-field control without writing boilerplate methods.

# Version
14

Increase this version number whenever this rule file changes.

# graphify Knowledge Graph (Optional Addon)

graphify turns a code folder into a queryable knowledge graph — god nodes, communities,
cross-file relationships, fan-in/fan-out. Use it to orient before grep and to spot god classes.

**Keep the build AST-only (no LLM, no API cost) by scoping to the code dir.** graphify runs a
free deterministic AST pass on *code* files, but a separate **LLM pass** on every *non-code*
file — docs, `.md`, `.txt`, config `.yaml`, images (vision), audio/video (whisper). That pass
needs an LLM (Gemini key or the host agent) and costs tokens. A build scoped to a pure-code dir
(`lib/`, `src/`, `app/`) has zero non-code files, so it skips the LLM pass entirely and rebuilds
need no AI. A repo-root build (`/graphify .`) sweeps in `docs/`, `README.md`, icons, and sound
assets — forcing the LLM pass. **Always scope to the code dir; never build the repo root.**

---

Setup instructions live in the coding-rules plugin at `graphify_setup_files/SETUP.md`.

## Folder layout (know which is which)

- `graphify-out/` at the **project root** = the **live graph** (`graph.json`, `GRAPH_REPORT.md`,
  `graph.html`). The only one queries read. Keep it `directed=True`.
- `graphify-out/cache/` at the project root = AST cache written by the CLI refresh (it runs
  with `GRAPHIFY_OUT` pointing at the root folder, see "Refreshing"). Scratch only.
- `<code-dir>/graphify-out/` = legacy AST cache from the skill build. Never the live graph
  under the documented flow; safe to delete. If a `graph.json` ever appears in there, a bare
  `graphify update` ran without `GRAPHIFY_OUT` — delete that `graph.json`, keep `cache/`.

## What the graph knows (and does not)

- Knows: code structure — classes, methods, calls, references, extends/implements, plus
  fan-in/fan-out and community / god-node structure.
- Does NOT know: business rules, API response shape, or rendered template/view output. It is a
  snapshot — stale until rebuilt. Constants referenced by string can appear as isolated nodes
  (AST limitation, not a missing dependency).

---

## Using the graph

- For codebase questions, run `graphify query "<question>"` first when `graphify-out/graph.json`
  exists. `graphify path "<A>" "<B>"` for relationships; `graphify explain "<concept>"` for a
  focused node. These return a small scoped subgraph vs. reading GRAPH_REPORT.md or raw grep.
- Judge coupling by direction: high **fan-in** + low fan-out (shared base / constants / DTO) is
  healthy; high **fan-out** (>~20 outgoing deps) is god-class risk and a refactor signal.
- Read `graphify-out/GRAPH_REPORT.md` only for broad architecture review, or when
  query/path/explain do not surface enough context.

## Manual refresh bat (`tools/graphify_update.bat`)

Copied from the `graphify_update.bat` template beside this addon, adjusted (`CODE_DIR`).
Run it from anywhere — it `pushd`es to the repo root itself.

- **Does:** (1) the live-graph CLI refresh from "Refreshing after a code change" in
  `IMPLEMENTATION_FLOW.md` (sets `GRAPHIFY_OUT` to the root
  `graphify-out\`, passes the absolute code dir); (2) smoke test — prints the root
  graph's `directed` flag + node count, `god-nodes`, a sample `query`.
- **Does NOT:** re-extract docs (see "Doc changes" in `IMPLEMENTATION_FLOW.md`) or build a first graph — that is the
  skill flow (`/graphify <code-dir> --directed`).
- **When to use:** after a code change outside an AI session, or as a "is graphify still
  wired up?" check after cloning, a dependency change, or a graphify upgrade.

## In-tree vendored code — exclude it, scoping alone won't

`--directed`-scoping the build to `<code-dir>` keeps external `vendor/`/`node_modules/` out
automatically, but a **committed** third-party library living *inside* `<code-dir>` (a bundled
SDK, a copied library folder) is not gitignored, so graphify scans it like first-party code.
Symptom: god-nodes / oversized communities in `GRAPH_REPORT.md` whose class names belong to a
library, not the app (e.g. hundreds of `Facebook*`/`GraphNode*` nodes from an in-tree Facebook
SDK).

Fix once per project:

1. Spot the vendored folder(s) under `<code-dir>` (e.g. `application/libs/`). Committed
   **asset/sprite dirs** are the same kind of noise — bundled UI images (jQuery-UI/colorbox
   sprites, e.g. `extensions/backend/assets/images/`) aren't code but graphify still scans them;
   exclude them the same way.
2. Drop a `.graphifyignore` at the scan root (gitignore syntax, honored by default):
   ```
   # Vendored / third-party code + bundled assets — not our architecture, noise in the graph
   libs/
   ```
3. Rebuild with the CLI refresh plus `--force` — a narrower corpus is a *smaller* graph,
   which trips the shrink guard (#479):
   `GRAPHIFY_OUT="$PWD/graphify-out" graphify update --force "$PWD/<code-dir>"`.
   Do NOT delete `graphify-out/graph.json` first (see "Refreshing after a code change" in
   `IMPLEMENTATION_FLOW.md`: the CLI would rebuild
   it undirected and drop the doc nodes).
4. Verify: grep the vendored library's distinctive class name in the new `graph.json` — it
   should return only first-party code that *uses* the library (e.g. your own `FacebookManager`),
   never the library's own classes.
