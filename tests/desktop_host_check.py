# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for Claude Desktop
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Claude Desktop (MCPB) host check. Standard library only (Python 3.8+); no account, no sign-in, no model calls.

1. Static: bundle/manifest.json against the MCPB manifest 0.4 rules (required fields, allowed keys, server type python, entry
   point present, ${__dirname} paths, Windows override, user_config, GPL-3.0-or-later, author), and its tool list against the
   server's tools/list.
2. Deterministic build: tools/build_mcpb.py twice gives the same sha256. The bundle has manifest.json at the root, the licence
   files, the icon, no caches or PDFs, fixed timestamps and permissions. The --manifest-version 0.3 and --windows-python variants
   are checked too.
3. With the official MCPB CLI (MCPB="npx --prefix <dir> mcpb" or `mcpb` on PATH): mcpb validate (0.4 and 0.3), mcpb pack of the
   staged tree gives the same contents as our bundle, mcpb info and mcpb unpack of our bundle.
4. Host-simulated Claude Desktop (there is no Claude Desktop for Linux): unpack the .mcpb into a fresh extensions folder,
   resolve mcp_config the way the MCPB spec says the app does (platform_overrides, ${__dirname}, ${user_config.workspace} with its
   ${HOME} default), start the server and run tests/e2e_mcp.py against it. Also runs the bundled CLI.

usage: python3 tests/desktop_host_check.py [REPO_DIR]"""
import hashlib, json, os, shlex, shutil, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = {"$schema", "dxt_version", "manifest_version", "name", "display_name", "version", "description", "long_description", "author",
       "repository", "homepage", "documentation", "support", "icon", "icons", "screenshots", "localization", "server", "tools",
       "tools_generated", "prompts", "prompts_generated", "keywords", "license", "privacy_policies", "compatibility", "user_config", "_meta"}


def main():
    repo = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
    ok = True

    def T(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond); print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- " + str(detail)[:700])); sys.stdout.flush()

    sys.dont_write_bytecode = True
    sys.path.insert(0, os.path.join(repo, "tools")); import build_mcpb  # noqa: E402
    m = json.load(open(os.path.join(repo, "bundle", "manifest.json"), encoding="utf-8"))
    srv = m.get("server", {}); mc = srv.get("mcp_config", {})
    T("manifest: MCPB 0.4, only schema keys, name/version/description/author, GPL-3.0-or-later",
      m.get("manifest_version") == "0.4" and set(m) <= TOP and m["name"] == "spindoctor-qwerty" and m["version"] == "1.1.0" and m["description"]
      and m["author"]["name"] == "RUSSELL PHILIP SMITHSON" and m["license"] == "GPL-3.0-or-later" and m["repository"]["url"].startswith("https://"), set(m) - TOP)
    T("server: type python, entry point present, args ${__dirname}/<entry>, win32 override, workspace from user_config",
      srv.get("type") == "python" and os.path.isfile(os.path.join(repo, "bundle", srv["entry_point"])) and mc["command"] == "python3"
      and mc["args"] == ["${__dirname}/" + srv["entry_point"]] and mc["platform_overrides"]["win32"] == {"command": "python"}
      and mc["env"]["SPINDOCTOR_WORKSPACE"] == "${user_config.workspace}", srv)
    uc = m["user_config"]["workspace"]
    T("user_config.workspace: directory, optional, default ${HOME}/spindoctor-workspace; compatibility python >=3.8, 3 platforms",
      uc["type"] == "directory" and uc["required"] is False and uc["default"] == "${HOME}/spindoctor-workspace"
      and m["compatibility"] == {"platforms": ["darwin", "win32", "linux"], "runtimes": {"python": ">=3.8"}}, uc)
    sys.path.insert(0, os.path.join(repo, "bundle", "server")); from spindoctor import api  # noqa: E402
    T("manifest tools == server tools (%d)" % len(api.TOOLS), [t["name"] for t in m["tools"]] == [t["name"] for t in api.TOOLS] and all(t.get("description") for t in m["tools"]))

    out, h1, n = build_mcpb.build(); _, h2, _ = build_mcpb.build()
    z = zipfile.ZipFile(out); names = z.namelist(); infos = z.infolist()
    T("deterministic build: same sha256 twice (%s), %d files" % (h1[:12], n), h1 == h2 and open(out + ".sha256").read().split()[0] == h1)
    T("bundle: manifest.json at root, LICENSE/NOTICE/COPYRIGHT/README/icon, engine, samples; no caches/PDFs; sorted, 1980 stamps, 0644",
      "manifest.json" in names and all(x in names for x in ("LICENSE", "NOTICE", "COPYRIGHT", "README.md", "icon.png", "server/spindoctor_mcp.py", "server/spindoctor/terminal.py", "server/spindoctor/data/SPINDOCTOR_PRESETS.json", "server/examples/theory/xbasis.q"))
      and not [x for x in names if x.endswith((".pyc", ".pdf")) or "__pycache__" in x] and names == sorted(names)
      and all(i.date_time == (1980, 1, 1, 0, 0, 0) and (i.external_attr >> 16) == 0o100644 for i in infos), names)
    icon = z.read("icon.png")
    T("icon.png: valid 512x512 PNG", icon[:8] == b"\x89PNG\r\n\x1a\n" and icon[16:24] == (512).to_bytes(4, "big") * 2)
    z.close()
    bm = json.loads(zipfile.ZipFile(build_mcpb.build("0.3", "py")[0]).read("manifest.json"))
    T("variant --manifest-version 0.3 --windows-python py", bm["manifest_version"] == "0.3" and "v0.3" in bm["$schema"] and bm["server"]["mcp_config"]["platform_overrides"]["win32"]["command"] == "py")
    stage03 = tempfile.mkdtemp(prefix="sdq_stage03_"); shutil.copytree(os.path.join(repo, "dist", "stage"), os.path.join(stage03, "s"))
    out, h3, _ = build_mcpb.build()
    T("rebuild default after variants restores the same sha256", h3 == h1)

    mcpb = os.environ.get("MCPB") or shutil.which("mcpb")
    st = os.path.join(repo, "dist", "stage"); work = tempfile.mkdtemp(prefix="sdq_mcpb_")
    if mcpb:
        run = lambda *a: subprocess.run(shlex.split(mcpb) + list(a), cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=300)
        ver = run("--version").stdout.strip().splitlines()[-1]
        r1 = run("validate", os.path.join(st, "manifest.json")); r2 = run("validate", os.path.join(stage03, "s", "manifest.json"))
        T("official mcpb CLI %s: validate passes (manifest 0.4 and the 0.3 variant)" % ver,
          r1.returncode == 0 and "validation passes" in r1.stdout and r2.returncode == 0 and "validation passes" in r2.stdout, r1.stdout + r2.stdout)
        r = run("pack", st, os.path.join(work, "packed.mcpb"))
        a = zipfile.ZipFile(out); b = zipfile.ZipFile(os.path.join(work, "packed.mcpb"))
        same = sorted(a.namelist()) == sorted(b.namelist()) and all(a.read(x) == b.read(x) for x in a.namelist())
        T("mcpb pack of the staged tree: same %d files and contents as tools/build_mcpb.py" % len(a.namelist()), r.returncode == 0 and same, r.stdout[-400:])
        r = run("info", out); T("mcpb info on our bundle", r.returncode == 0 and "spindoctor-qwerty" in r.stdout, r.stdout)
        r = run("unpack", out, os.path.join(work, "unpacked"))
        T("mcpb unpack on our bundle", r.returncode == 0 and os.path.isfile(os.path.join(work, "unpacked", "manifest.json")), r.stdout)
    else:
        print("SKIP official mcpb CLI not found (set MCPB='npx --prefix <dir> mcpb')")

    ext = os.path.join(tempfile.mkdtemp(prefix="sdq_claude_desktop_"), "Claude Extensions", "local.mcpb.russell-philip-smithson.spindoctor-qwerty")
    zipfile.ZipFile(out).extractall(ext)
    home = tempfile.mkdtemp(prefix="sdq_home_")
    um = json.load(open(os.path.join(ext, "manifest.json"), encoding="utf-8"))["server"]["mcp_config"]
    cfg = dict(um); cfg.update(um.get("platform_overrides", {}).get(sys.platform, {}))
    ws = m["user_config"]["workspace"]["default"].replace("${HOME}", home)
    sub = lambda s: s.replace("${__dirname}", ext).replace("${user_config.workspace}", ws).replace("${HOME}", home).replace("${/}", os.sep).replace("${pathSeparator}", os.sep)
    cmd = [os.environ.get("SPINDOCTOR_PYTHON") or sub(cfg["command"])] + [sub(x) for x in cfg["args"]]
    env = dict(os.environ, **{k: sub(v) for k, v in cfg.get("env", {}).items()})
    r = subprocess.run([cmd[0], os.path.join(ext, "server", "spindoctor_cli.py"), "functions", "gates"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, timeout=120)
    T("bundled CLI inside the unpacked extension (functions gates)", r.returncode == 0 and "| " in r.stdout, r.stdout[-300:])
    r = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server"] + cmd + ["--examples", os.path.join(ext, "server", "examples", "theory"),
                        "--out", os.path.join(work, "e2e_results.json")], env=env)
    T("MCP end-to-end through the unpacked .mcpb, mcp_config resolved as Claude Desktop does (workspace %s)" % ws.replace(home, "${HOME}"),
      r.returncode == 0)
    msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "claude-desktop-sim", "version": "0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "spindoctor_run_script", "arguments": {"script": "q.circuit new ws 1\nq.circuit add h 0\nq.circuit run shots 10 basis z"}}}]
    r = subprocess.run(cmd, input="".join(json.dumps(x) + "\n" for x in msgs), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=120)
    pdfs = [f for _, _, fs in os.walk(ws) for f in fs if f.endswith(".pdf")]
    T("a tool call without a workspace argument writes its reports into the user_config workspace (%d PDFs)" % len(pdfs), '"id": 2' in r.stdout.replace('"id":2', '"id": 2') and pdfs, r.stdout[-400:] + r.stderr[-300:])
    print("HOST-CHECK (host-simulated Claude Desktop; official mcpb CLI %s)" % ("used" if mcpb else "not found"), "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
