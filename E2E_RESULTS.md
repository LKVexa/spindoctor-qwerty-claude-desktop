# End-to-end results: spindoctor-qwerty-claude-desktop 1.1.0

Run on 2026-10-10 (PT) in a clean-room copy (empty folder, empty HOME, minimal PATH, no access to engine development folders),
following only this README: `python3 tools/build_mcpb.py`, then `tests/desktop_host_check.py`.

**Mode:** host-simulated Claude Desktop. Claude Desktop has no Linux build, so it can't be installed on the test machine. The
**official MCPB CLI 2.1.2** (`npm i @anthropic-ai/mcpb`, no account) validated, packed, inspected and unpacked the bundle. The
`.mcpb` was then unpacked into a fresh extensions folder, and `mcp_config` was resolved as the MCPB spec says Claude Desktop does
(`${__dirname}`, `platform_overrides`, `${user_config.workspace}` with its `${HOME}` default) before the full end-to-end
suite ran against that server.

**Manifest:** MCPB 0.4 (`LATEST_MANIFEST_VERSION` in mcpb 2.1.2). The 0.3 build variant also validates.

**Bundle built in the clean room:** `dist/spindoctor-qwerty.mcpb`, 41 files, sha256 `042893be775ec3d6985ffba9b549f279661367f06ba8451732f8564dfd95350a`. The bundle is identical for the
same sources and Python/zlib build. It isn't committed because it's a binary build output.

**Parity target:** the updated SpinDoctor 3.1.2. Publishing was approved by Russell on the basis of the updated 3.1.2
passing its own suite 18/18, with the three 29-qubit test checks adapted to the 298-qubit limit.

## Host check (clean room)

```
PASS manifest: MCPB 0.4, only schema keys, name/version/description/author, GPL-3.0-or-later
PASS server: type python, entry point present, args ${__dirname}/<entry>, win32 override, workspace from user_config
PASS user_config.workspace: directory, optional, default ${HOME}/spindoctor-workspace; compatibility python >=3.8, 3 platforms
PASS manifest tools == server tools (6)
PASS deterministic build: same sha256 twice (042893be775e), 41 files
PASS bundle: manifest.json at root, LICENSE/NOTICE/COPYRIGHT/README/icon, engine, samples; no caches/PDFs; sorted, 1980 stamps, 0644
PASS icon.png: valid 512x512 PNG
PASS variant --manifest-version 0.3 --windows-python py
PASS rebuild default after variants restores the same sha256
PASS official mcpb CLI 2.1.2: validate passes (manifest 0.4 and the 0.3 variant)
PASS mcpb pack of the staged tree: same 41 files and contents as tools/build_mcpb.py
PASS mcpb info on our bundle
PASS mcpb unpack on our bundle
PASS bundled CLI inside the unpacked extension (functions gates)
PASS initialize (server spindoctor-qwerty 1.1.0)
PASS tools/list exposes the 6 tools
PASS function table (Markdown, 19 sections, 298-qubit limits listed)
PASS 241 presets listed
PASS one script per command family (16 families, every table example)
PASS 298-qubit circuit with mcx7 (prepared-factor-Born-Z)
PASS q.folder on mixed .txt/.csv/.json/.qasm folder (+ .md skipped)
PASS theory from a file -> supported, TXT+PDF report
PASS theory from a chat summary + quoted excerpts -> supported
PASS theory from an exported chat transcript -> supported
PASS presets qc-001..qc-025 match the updated 3.1.2 reference (20 identical, 5 documented differences)
PASS TXT+PDF reports valid (255 PDFs, 255 TXT twins)
SUMMARY 12/12 passed in 14.2s
PASS MCP end-to-end through the unpacked .mcpb, mcp_config resolved as Claude Desktop does (workspace ${HOME}/spindoctor-workspace)
PASS a tool call without a workspace argument writes its reports into the user_config workspace (3 PDFs)
HOST-CHECK (host-simulated Claude Desktop; official mcpb CLI used) PASS
```

The five documented preset differences are the engine's known, accepted ones (CPU-only reference instead of OpenCL GPU
fields, tranche checkpoint text, state file name), as in every SpinDoctor Qwerty repo.
