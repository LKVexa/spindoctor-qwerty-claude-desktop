# SpinDoctor Qwerty for Claude Desktop

A one-click **Claude Desktop extension** (MCP Bundle, `.mcpb`) for the SpinDoctor 3.1.2 quantum-circuit **simulator**. Install
it, pick a workspace folder, and Claude Desktop gets six local tools: the function table, q.* scripts, the 241 presets, preset
search, reports, and theory testing. Nothing to configure by hand, no JSON to edit, nothing downloaded.

Engine: SpinDoctor Qwerty 1.1.0 (SpinDoctor 3.1.2 parity), bundled under `bundle/server/`. Standard-library Python 3.8+ only,
NumPy optional. Manifest: MCPB **0.4**, the newest version the official `mcpb` CLI (2.1.2) validates and packs.

## Which SpinDoctor Qwerty repository should I use?

| You use... | Choose |
| --- | --- |
| **Claude Desktop** chat and want the tools with one click (Settings > Extensions) | **this repo** |
| claude.ai chat or Cowork (`.plugin` upload), or one plugin for claude.ai, Cowork and Claude Code | [spindoctor-qwerty-claude](https://github.com/LKVexa/spindoctor-qwerty-claude) |
| Claude Code in a terminal: slash commands, a subagent, CLI-first workflow | [spindoctor-qwerty-claude-code](https://github.com/LKVexa/spindoctor-qwerty-claude-code) |

All three bundle the same engine and give the same results. This one is tools only: Claude Desktop extensions have no skills,
slash commands or agents, so Claude learns the tools from their descriptions and the function table.

## Build the .mcpb

The `.mcpb` is a ZIP file, so it isn't committed. Build it from this repo (Python 3.8+, no packages, a second or so):

```bash
git clone https://github.com/LKVexa/spindoctor-qwerty-claude-desktop
cd spindoctor-qwerty-claude-desktop
python3 tools/build_mcpb.py          # on Windows: python tools/build_mcpb.py
```

This writes `dist/spindoctor-qwerty.mcpb` and `dist/spindoctor-qwerty.mcpb.sha256`. The build is deterministic: entries are
sorted and timestamps and permissions are fixed, so the same sources give the same bundle, and the same SHA-256 with the same
Python build. Options:

- `--windows-python py`: the command Claude Desktop uses to start Python on Windows (default `python`; macOS and Linux use
  `python3`). Use `py` if you only have the Python launcher, or a full path such as `"C:/Python312/python.exe"`.
- `--manifest-version 0.3`: if your Claude Desktop is older and refuses manifest 0.4 (this bundle uses nothing that is new in
  0.4).

Optional check with the official CLI (needs Node.js): `npx @anthropic-ai/mcpb validate dist/stage/manifest.json`. Use the build
script rather than running `mcpb pack bundle` directly, because the script also adds the icon and the licence files.

## Install in Claude Desktop

1. You need Python 3.8 or newer. On macOS and Linux it must answer to `python3`. On Windows it must answer to `python` (the
   python.org installer with "Add python.exe to PATH" ticked, or the Microsoft Store Python), or rebuild with `--windows-python`.
2. Double-click `dist/spindoctor-qwerty.mcpb`, or open Claude Desktop > Settings > Extensions and drag the file in.
3. Click Install. Optionally choose the **SpinDoctor workspace** folder (default `~/spindoctor-workspace`). Every report goes
   there.
4. Enable the extension and ask: "What can SpinDoctor do?"

Claude Desktop shows the bundle as unsigned (it is). The sha256 file lets you check that the file is the one you built.

## What you can ask

- "Show the SpinDoctor function table" or "show the gates": `spindoctor_functions`.
- "Build a Bell pair and run 1000 shots": `spindoctor_run_script` with q.* commands.
- "Run preset qc-061 with 500 shots" or "which presets are about Grover?": `spindoctor_run_preset`, `spindoctor_list_presets`.
- "Run every command file in C:/Users/me/runs/batch1": `q.folder run path=...` through `spindoctor_run_script`.
- "Show the last report": `spindoctor_report`.
- "Test the theory in C:/Users/me/notes/theory.md" or "test the theory we discussed": `spindoctor_test_theory`.

**Files and attachments:** an extension can't see files you drop into the Claude Desktop chat. Give the file's path on your
computer, or let Claude pass the text (source `text`). For "the theory we discussed", Claude summarises the claims,
assumptions, variables and a measurable prediction, asks you to confirm, and passes short quoted excerpts. The plugin can't read
the chat by itself, and very long chats may already be cut by the context window.

## Function table

The full table (every command family with runnable examples, the gates, the six tools and all 241 presets) is in
[FUNCTIONS.md](FUNCTIONS.md). Ask for it in chat at any time.

| Tool | What it does |
| --- | --- |
| `spindoctor_functions` | The function table (Function, What it does, Command to type), by section with an optional filter |
| `spindoctor_run_script` | Runs q.* commands; returns results plus TXT/PDF/JSON/CSV report paths |
| `spindoctor_run_preset` | Runs one of the 241 presets (qc-001..qc-241) with optional overrides |
| `spindoctor_list_presets` | Lists or filters the presets |
| `spindoctor_report` | Lists or reads reports in the workspace |
| `spindoctor_test_theory` | Tests a theory from a file, pasted text or the chat, and writes a theory test report |

## Theory testing

Files can be .txt, .md, .pdf, .py, .json, .csv or .q, and exported chat transcripts (.txt, .md, .json, .html) also work. The
theory test report (TXT + JSON + PDF) gives the hypothesis, the q.* script, the raw results, a verdict (supported, not
supported or inconclusive) and the limits. Samples are in `bundle/server/examples/theory/`, and inside the installed extension.

## Honest limits

- SpinDoctor is a **classical FP64 simulator** running on your computer. It is not a quantum computer and gives no quantum
  speed-up or advantage.
- 1-298 logical qubits per register. An entangled block (factor) is capped at 59 qubits, and memory grows as 2^n x 16 bytes
  for an n-qubit dense block, so a memory budget applies. Registers wider than 29 qubits sample in basis z only.
- `q.compile synthesize` (preset qc-198) is not available, as in SpinDoctor 3.1.2.
- Python 3.8 or newer must be installed. Claude Desktop does not ship Python for `python` type extensions. NumPy is used if
  present, but nothing is installed.
- `q.folder` reads only the top level of a folder: 1-128 supported files, 4 MiB per file, 1-128 commands per file, 4096
  characters per command, strict UTF-8, and it stops at the first failing file.
- The bundle is unsigned. Manifest 0.4 is marked experimental by the MCPB project. The only 0.4 addition (the `uv` server
  type) isn't used here, which is why the 0.3 fallback is identical in behaviour.

## Testing

`python3 tests/desktop_host_check.py` (set `MCPB="npx --prefix <dir> mcpb"` to include the official CLI). It checks the
manifest against the MCPB 0.4 rules and the server's tool list, builds the bundle twice (same SHA-256), checks its contents,
icon and the build variants, and runs `mcpb validate`, `mcpb pack` (same contents as our build), `mcpb info` and `mcpb unpack`
with the official CLI. Claude Desktop has no Linux build and can't be installed on the test machine, so the host is
**host-simulated**: the `.mcpb` is unpacked into a fresh extensions folder, `mcp_config` is resolved as the MCPB spec says
Claude Desktop does it (`${__dirname}`, platform overrides, `${user_config.workspace}` with its `${HOME}` default), and the full
end-to-end suite runs against that server. See [E2E_RESULTS.md](E2E_RESULTS.md).

## Layout

```
bundle/manifest.json        MCPB 0.4 manifest (source of truth)
bundle/server/              MCP server, CLI, SpinDoctor engine, sample theory files
tools/build_mcpb.py         deterministic .mcpb builder (adds icon.png, README, LICENSE, NOTICE, COPYRIGHT)
tests/                      host check and end-to-end suite
dist/                       build output (git-ignored)
```

## Author and license

Author: RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later
(`GPL-3.0-or-later`); see [LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). The built `.mcpb` carries the same
licence files.
