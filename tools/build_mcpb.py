# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for Claude Desktop
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Build the Claude Desktop extension, dist/spindoctor-qwerty.mcpb, deterministically. Standard library only (Python 3.8+).

  python3 tools/build_mcpb.py                         # dist/spindoctor-qwerty.mcpb + .sha256
  python3 tools/build_mcpb.py --windows-python py     # Windows command to start Python (default: python)
  python3 tools/build_mcpb.py --manifest-version 0.3  # for an older Claude Desktop that doesn't know manifest 0.4

What goes in (an MCPB bundle is a ZIP with manifest.json at its root): bundle/manifest.json, bundle/server/ (the MCP server, the
CLI and the SpinDoctor engine), the sample theory files, a generated icon.png, and README.md, LICENSE, NOTICE, COPYRIGHT.
Left out: __pycache__, *.pyc, generated PDFs. Entries are sorted, timestamps fixed (1980-01-01), permissions fixed (0644), so
the same sources give the same files. The archive bytes are identical for the same Python/zlib build. The staged tree is kept
in dist/stage/ so you can check it with the official CLI: `npx @anthropic-ai/mcpb validate dist/stage/manifest.json`
(`mcpb pack dist/stage` gives an equivalent but not byte-identical bundle).
"""
import argparse, hashlib, json, os, shutil, struct, sys, zipfile, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
NAME = "spindoctor-qwerty.mcpb"
EXTRA = ("README.md", "LICENSE", "NOTICE", "COPYRIGHT")
STAMP = (1980, 1, 1, 0, 0, 0)


def icon_png(size=512):
    """A small deterministic icon: a Bloch-sphere ring with a spin arrow on a dark rounded square."""
    import math
    c = (size - 1) / 2.0; R = size * 0.36; rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            dx, dy = x - c, y - c
            corner = max(abs(dx), abs(dy)) - size * 0.40
            inside = corner <= 0 or math.hypot(max(abs(dx) - size * 0.40, 0), max(abs(dy) - size * 0.40, 0)) <= size * 0.08
            if not inside: row += bytes((0, 0, 0, 0)); continue
            px = [18, 24, 48, 255]; r = math.hypot(dx, dy)
            if abs(r - R) < size * 0.018: px = [90, 210, 255, 255]                          # sphere outline
            elif abs(math.hypot(dx, dy / 0.32) - R) < size * 0.03 and r < R: px = [60, 120, 190, 255]   # equator
            ax, ay = size * 0.20, -size * 0.24                                                # spin vector
            t = max(0.0, min(1.0, (dx * ax + dy * ay) / (ax * ax + ay * ay)))
            if math.hypot(dx - t * ax, dy - t * ay) < size * 0.022: px = [255, 196, 64, 255]
            if math.hypot(dx - ax, dy - ay) < size * 0.05: px = [255, 196, 64, 255]
            if r < size * 0.03: px = [255, 255, 255, 255]
            row += bytes(px)
        rows.append(bytes(row))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b""))


def stage(manifest_version="0.4", windows_python="python"):
    st = os.path.join(DIST, "stage")
    shutil.rmtree(st, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "bundle"), st, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "*.pdf"))
    for f in EXTRA: shutil.copyfile(os.path.join(ROOT, f), os.path.join(st, f))
    m = json.load(open(os.path.join(st, "manifest.json"), encoding="utf-8"))
    if manifest_version != m["manifest_version"]:
        m["manifest_version"] = manifest_version
        m["$schema"] = m["$schema"].replace("v0.4", "v" + manifest_version)
    m["server"]["mcp_config"]["platform_overrides"]["win32"]["command"] = windows_python
    open(os.path.join(st, "manifest.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    open(os.path.join(st, m["icon"]), "wb").write(icon_png())
    return st


def files(st):
    out = []
    for r, ds, fs in os.walk(st):
        ds[:] = sorted(ds)
        out += [os.path.join(r, f) for f in sorted(fs)]
    return sorted(out, key=lambda p: os.path.relpath(p, st).replace(os.sep, "/"))


def build(manifest_version="0.4", windows_python="python"):
    st = stage(manifest_version, windows_python)
    out = os.path.join(DIST, NAME)
    with zipfile.ZipFile(out, "w") as z:
        for p in files(st):
            zi = zipfile.ZipInfo(os.path.relpath(p, st).replace(os.sep, "/"), STAMP)
            zi.external_attr = 0o100644 << 16; zi.create_system = 3; zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, open(p, "rb").read(), compresslevel=9)
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()
    open(out + ".sha256", "w", newline="\n").write("%s  %s\n" % (h, NAME))
    return out, h, len(files(st))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest-version", choices=("0.4", "0.3"), default="0.4")
    ap.add_argument("--windows-python", default="python", help="command Claude Desktop uses to start Python on Windows")
    a = ap.parse_args()
    if any(ch in a.windows_python for ch in '"\'`$;&|<>\n'): ap.error("--windows-python must be a plain program name or path")
    out, h, n = build(a.manifest_version, a.windows_python)
    print("%s  (%d files, %d bytes)\nsha256 %s" % (os.path.relpath(out, ROOT), n, os.path.getsize(out), h))


if __name__ == "__main__":
    sys.exit(main())
