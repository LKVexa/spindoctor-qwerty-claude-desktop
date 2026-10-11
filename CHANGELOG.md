# Changelog

## 1.1.0 (2026-10-10)

- Engine 1.1.0 at SpinDoctor 3.1.2 parity: 1-298 logical qubits (59 per factor), `mcx7`, wide basis-z sampling, `q.folder`
  (with .qasm2/.circuit and skipped-file listing), CSV report copies, measurement-CSV fitting, all 241 presets replayed
  against the updated 3.1.2 reference outputs.
- New tools: `spindoctor_functions` (function table) and `spindoctor_test_theory` (files, pasted text, chat summaries).
- Manifest moved from MCPB 0.3 to 0.4, the newest version the official mcpb CLI 2.1.2 validates and packs. A 0.3 fallback is
  available with `--manifest-version 0.3`.
- Windows: `platform_overrides.win32` starts `python` (1.0 used `python3`, which the python.org installer doesn't provide).
  Can be changed with `--windows-python`.
- Workspace: user_config default now uses the documented `${HOME}` variable. Added `PYTHONUTF8` and `PYTHONDONTWRITEBYTECODE`.
- Added the long description (honest limits, 298-qubit text instead of 29), repository/homepage/documentation/support links,
  a generated 512x512 icon, and tool descriptions that match the server.
- The committed `.mcpb` is replaced by `tools/build_mcpb.py`, a deterministic builder (sorted entries, fixed timestamps and
  permissions; same SHA-256 twice). The bundle now carries README, LICENSE, NOTICE and COPYRIGHT.
- Licence changed from MIT to GPL-3.0-or-later, with NOTICE, COPYRIGHT and SPDX headers. Author is RUSSELL PHILIP SMITHSON.
- Tests: `tests/desktop_host_check.py` (official mcpb CLI + host-simulated Claude Desktop + full MCP end-to-end).

## 1.0.0

- Initial Claude Desktop bundle (manifest 0.3, committed .mcpb).
