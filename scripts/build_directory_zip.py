#!/usr/bin/env python3
"""Build a directory submission without modifying the full marketplace plugin."""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

REPO = Path(__file__).resolve().parents[1]
MANIFEST = ".codex-plugin/plugin.json"


def read_file(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file, not a symlink: {path}")
    return path.read_bytes()


def require_object(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def validate_local_mcp(mcp):
    servers = require_object(mcp, "MCP configuration").get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        raise ValueError("Local MCP mode requires at least one server")
    for server in servers.values():
        require_object(server, "MCP server")
        command = server.get("command")
        if not isinstance(command, str) or not command.strip() or "url" in server:
            raise ValueError("Local MCP mode accepts stdio servers only")
        args = server.get("args", [])
        if not isinstance(args, list) or any(not isinstance(arg, str) for arg in args):
            raise ValueError("MCP args must be an array of strings")
        cwd = server.get("cwd", "")
        if not isinstance(cwd, str):
            raise ValueError("MCP cwd must be a string")
        for value in (command, cwd, *args):
            path = value.split("=", 1)[-1] if value.startswith("-") else value
            if (path in (".", "..") or path.startswith(("/", "\\", "~", "./", "../", ".\\", "..\\"))
                    or re.match(r"^[A-Za-z]:", path)):
                raise ValueError("MCP command, args and cwd must not contain machine-local paths")
        env = require_object(server.get("env", {}), "MCP env")
        if any(not isinstance(value, str) or not re.fullmatch(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}", value)
               for value in env.values()):
            raise ValueError("MCP env values must be ${VARIABLE} references, not literal values")


def build(repo, output, include_local_mcp=False):
    source = repo / "plugins/altimate-code"
    manifest = require_object(json.loads(read_file(source / MANIFEST)), "Manifest")
    version = manifest["version"]
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?", version):
        raise ValueError("Manifest version must be a semantic version")
    if (source / "plugin.json").exists():
        raise ValueError("Keep the source in the legacy .codex-plugin format")
    interface = require_object(manifest["interface"], "Manifest interface")
    for field in ("displayName", "shortDescription"):
        if not isinstance(interface.get(field), str) or not 1 <= len(interface[field]) <= 30:
            raise ValueError(f"interface.{field} must contain 1–30 characters")
    prompts = interface.get("defaultPrompt", [])
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        raise ValueError("Provide 1–3 default prompts")
    if any(not isinstance(p, str) or not 1 <= len(p) <= 128 or "@" in p for p in prompts) or len(set(prompts)) != len(prompts):
        raise ValueError("Default prompts must be unique strings of 1–128 characters without @mentions")
    for field in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        if not isinstance(interface.get(field), str) or not interface[field].startswith("https://"):
            raise ValueError(f"interface.{field} must be an HTTPS URL")

    # Only portable skills and images belong in the directory artifact. No blanket
    # copy of the source tree: future hooks, scripts, app references and secrets
    # must not accidentally become part of a public upload.
    files = {}
    for directory in ("skills", "assets"):
        root = source / directory
        if root.is_symlink() or not root.is_dir():
            raise ValueError(f"Missing regular {directory} directory")
        for path in sorted(root.rglob("*")):
            relative = path.relative_to(source)
            if path.is_symlink():
                raise ValueError(f"Symlinks are not allowed: {relative}")
            if path.is_dir():
                continue
            if any(part.startswith(".") for part in relative.parts):
                raise ValueError(f"Hidden files are not allowed: {relative}")
            allowed = {".md"} if directory == "skills" else {".svg", ".png", ".jpg", ".jpeg", ".webp"}
            if path.suffix.lower() not in allowed:
                raise ValueError(f"Unsupported directory package file: {relative}")
            files[relative.as_posix()] = read_file(path)

    def require_packaged(path):
        if not isinstance(path, str) or not path.startswith("./") or path[2:] not in files:
            raise ValueError(f"Missing packaged resource: {path}")

    for field in ("logo", "composerIcon"):
        require_packaged(interface.get(field))
        path = interface[field][2:]
        if not path.endswith(".svg"):
            raise ValueError("This builder validates SVG listing icons; add validation before using raster icons")
        data = files[path]
        if len(data) > 5 * 1024 * 1024:
            raise ValueError("Listing icons must be at most 5 MiB")
        try:
            icon = ET.fromstring(data)
            width, height = float(icon.attrib["width"]), float(icon.attrib["height"])
        except (ET.ParseError, KeyError, ValueError) as error:
            raise ValueError("Listing SVGs require numeric width and height") from error
        if icon.tag != "{http://www.w3.org/2000/svg}svg" or width != height or not width >= 48:
            raise ValueError("Listing icons must be square SVGs at least 48px wide")
    extensions = require_object(manifest.setdefault("extensions", {}), "Manifest extensions")
    extension = require_object(extensions.setdefault("com.openai", {}), "OpenAI extension")
    require_packaged(extension.get("onboardingSkill"))
    for holder in (manifest, extension):
        for key in ("hooks", "commands", "apps", "mcpServers"):
            holder.pop(key, None)
    manifest["requires_local_executor"] = True
    manifest["skills"] = "./skills/"
    if include_local_mcp:
        mcp = json.loads(read_file(source / ".mcp.json"))
        validate_local_mcp(mcp)
        files[".mcp.json"] = (json.dumps(mcp, indent=2) + "\n").encode()
        manifest["mcpServers"] = "./.mcp.json"
    files[MANIFEST] = (json.dumps(manifest, indent=2) + "\n").encode()
    for name in ("LICENSE", "PRIVACY.md", "TERMS.md", "SECURITY.md"):
        files[name] = read_file(repo / name)
    files["README.md"] = read_file(repo / "DIRECTORY.md")

    mode = "-local-mcp" if include_local_mcp else ""
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"altimate-code-{version}{mode}.zip"
    # Fixed timestamps, order and permissions make the same source reproducible.
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPO / "dist")
    parser.add_argument(
        "--include-local-mcp", action="store_true",
        help="Include stdio MCP only after OpenAI confirms organization allowlisting",
    )
    args = parser.parse_args()
    try:
        target = build(REPO, args.output_dir, args.include_local_mcp)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Directory build failed: {error}\n")
    print(target)
    print("Package built; this does not establish OpenAI submission eligibility or approval.")


if __name__ == "__main__":
    main()
