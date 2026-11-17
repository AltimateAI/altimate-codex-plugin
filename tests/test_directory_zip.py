"""Exercise upload artifacts, not just the manifest transformation."""

import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZipFile

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("builder", REPO / "scripts/build_directory_zip.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class DirectoryZipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.source = self.repo / "plugins/altimate-code"
        shutil.copytree(REPO / "plugins/altimate-code", self.source)
        for name in ("LICENSE", "PRIVACY.md", "TERMS.md", "SECURITY.md", "DIRECTORY.md"):
            shutil.copyfile(REPO / name, self.repo / name)
        self.out = Path(self.temp.name) / "dist"

    def manifest(self):
        return json.loads((self.source / builder.MANIFEST).read_text())

    def save_manifest(self, manifest):
        (self.source / builder.MANIFEST).write_text(json.dumps(manifest))

    def test_real_cli_build_and_archive_contract(self):
        before = {p.relative_to(REPO): p.read_bytes() for p in
                  (REPO / "plugins/altimate-code").rglob("*") if p.is_file()}
        subprocess.run(["python3", str(REPO / "scripts/build_directory_zip.py"),
                        "--output-dir", str(self.out)], check=True, capture_output=True)
        archives = list(self.out.glob("*.zip"))
        self.assertEqual(len(archives), 1)
        with ZipFile(archives[0]) as archive:
            names = set(archive.namelist())
            self.assertIn(".codex-plugin/plugin.json", names)
            self.assertNotIn("plugin.json", names)
            self.assertNotIn(".mcp.json", names)
            self.assertNotIn(".app.json", names)
            self.assertFalse(any(n.startswith(("hooks/", "commands/", "scripts/")) for n in names))
            manifest = json.loads(archive.read(builder.MANIFEST))
            self.assertTrue(manifest["requires_local_executor"])
            for holder in (manifest, manifest["extensions"]["com.openai"]):
                self.assertFalse(set(holder) & {"hooks", "commands", "apps", "mcpServers"})
            self.assertLessEqual(len(manifest["interface"]["shortDescription"]), 30)
            self.assertLessEqual(len(manifest["interface"]["defaultPrompt"]), 3)
            for field in ("logo", "composerIcon"):
                image = ET.fromstring(archive.read(manifest["interface"][field][2:]))
                self.assertEqual(image.attrib["width"], image.attrib["height"])
                self.assertGreaterEqual(int(image.attrib["width"]), 48)
            for path in (REPO / "plugins/altimate-code/skills").rglob("*.md"):
                self.assertEqual(archive.read(path.relative_to(REPO / "plugins/altimate-code").as_posix()), path.read_bytes())
            self.assertIn(manifest["extensions"]["com.openai"]["onboardingSkill"][2:], names)
            for name in ("LICENSE", "PRIVACY.md", "TERMS.md", "SECURITY.md"):
                self.assertEqual(archive.read(name), (REPO / name).read_bytes())
            self.assertEqual(archive.read("README.md"), (REPO / "DIRECTORY.md").read_bytes())
        self.assertTrue(all((REPO / p).read_bytes() == data for p, data in before.items()))
        self.assertTrue((REPO / "plugins/altimate-code/hooks/hooks.json").exists())

    def test_reproducible(self):
        target = builder.build(self.repo, self.out)
        first = target.read_bytes()
        self.assertEqual(builder.build(self.repo, self.out).read_bytes(), first)

    def test_listing_artwork_matches_official_source(self):
        # Hash of the unmodified content after the outer opening SVG tag in
        # altimate-frontend's altimate_logo.svg, revision documented in DIRECTORY.md.
        expected = "41237a050140116a0cde5beb481a572a0ef1cf70c9488ad1c620d13a0de26b12"
        for name in ("logo", "composer-icon"):
            svg = (self.source / f"assets/{name}.svg").read_text()
            self.assertEqual(hashlib.sha256(svg[svg.index(">") + 1:].encode()).hexdigest(), expected)

    def test_mcp_only_on_explicit_opt_in_and_separate_artifact(self):
        mcp = {"mcpServers": {"altimate-code": {"command": "altimate-code", "args": ["mcp", "serve", "--workspace-tools"]}}}
        (self.source / ".mcp.json").write_text(json.dumps(mcp))
        manifest = self.manifest()
        manifest.update({"mcpServers": "./.mcp.json", "apps": "./.app.json", "hooks": "./hooks/hooks.json"})
        manifest["extensions"]["com.openai"].update({"mcpServers": "./.mcp.json", "apps": "./.app.json", "hooks": "./hooks/hooks.json"})
        self.save_manifest(manifest)
        (self.source / ".app.json").write_text('{"apps": {}}')
        ordinary = builder.build(self.repo, self.out)
        local = builder.build(self.repo, self.out, True)
        self.assertNotEqual(ordinary, local)
        with ZipFile(ordinary) as archive:
            self.assertNotIn(".mcp.json", archive.namelist())
            self.assertNotIn("mcpServers", json.loads(archive.read(builder.MANIFEST)))
        with ZipFile(local) as archive:
            self.assertEqual(json.loads(archive.read(".mcp.json")), mcp)
            self.assertEqual(json.loads(archive.read(builder.MANIFEST))["mcpServers"], "./.mcp.json")
            self.assertNotIn(".app.json", archive.namelist())

    def test_mcp_mode_rejects_missing_and_remote_server(self):
        with self.assertRaises((ValueError, OSError)):
            builder.build(self.repo, self.out, True)
        (self.source / ".mcp.json").write_text('{"mcpServers":{"remote":{"url":"https://example.com/mcp"}}}')
        with self.assertRaises(ValueError):
            builder.build(self.repo, self.out, True)

    def test_invalid_metadata_fails_without_archive(self):
        original = self.manifest()
        for field, value in (("shortDescription", "x" * 31), ("displayName", "x" * 31),
                             ("defaultPrompt", ["x"] * 4), ("defaultPrompt", ["x" * 129]),
                             ("defaultPrompt", ["Ask @altimate for help"]), ("logo", "../secret.svg"),
                             ("supportURL", "http://example.com")):
            with self.subTest(field=field):
                manifest = json.loads(json.dumps(original))
                manifest["interface"][field] = value
                self.save_manifest(manifest)
                with self.assertRaises(ValueError):
                    builder.build(self.repo, self.out)
        self.assertFalse(self.out.exists())

    def test_missing_onboarding_rejected(self):
        (self.source / "skills/get-started/SKILL.md").unlink()
        with self.assertRaises(ValueError):
            builder.build(self.repo, self.out)

    def test_mcp_rejects_literal_environment_values_without_exposing_them(self):
        for env in ({"TOKEN": "synthetic-secret"}, {"TOKEN": "prefix-${TOKEN}"},
                    {"TOKEN": 7}, {"TOKEN": None}, [], None):
            with self.subTest(env=env):
                config = {"mcpServers": {"example": {"command": "example", "env": env}}}
                (self.source / ".mcp.json").write_text(json.dumps(config))
                with self.assertRaises(ValueError) as error:
                    builder.build(self.repo, self.out, True)
                self.assertNotIn("synthetic-secret", str(error.exception))
                self.assertFalse(self.out.exists())
        config["mcpServers"]["example"]["env"] = {"TOKEN": "${TOKEN}"}
        (self.source / ".mcp.json").write_text(json.dumps(config))
        with ZipFile(builder.build(self.repo, self.out, True)) as archive:
            self.assertEqual(json.loads(archive.read(".mcp.json")), config)

    def test_mcp_rejects_machine_local_paths(self):
        for field, value in (("command", "/Users/example/bin/mcp"),
                             ("args", ["--config=/Users/example/config.json"]),
                             ("args", [r"C:\Users\example\config.json"]),
                             ("cwd", "~/workspace")):
            with self.subTest(field=field, value=value):
                server = {"command": "example", field: value}
                (self.source / ".mcp.json").write_text(json.dumps({"mcpServers": {"example": server}}))
                with self.assertRaises(ValueError):
                    builder.build(self.repo, self.out, True)
                self.assertFalse(self.out.exists())

    def test_malformed_metadata_cli_errors_are_friendly(self):
        script = self.repo / "scripts/build_directory_zip.py"
        script.parent.mkdir()
        shutil.copyfile(REPO / "scripts/build_directory_zip.py", script)
        original = self.manifest()
        malformed = [[], {**original, "version": 123}, {**original, "interface": []},
                     {**original, "interface": {**original["interface"], "websiteURL": None}},
                     {**original, "extensions": []},
                     {**original, "extensions": {"com.openai": None}}]
        for manifest in malformed:
            with self.subTest(manifest=manifest):
                self.save_manifest(manifest)
                result = subprocess.run(["python3", str(script), "--output-dir", str(self.out)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn("Directory build failed:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(self.out.exists())

    def test_non_square_icon_rejected(self):
        (self.source / "assets/logo.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="256" height="128"/>')
        with self.assertRaises(ValueError):
            builder.build(self.repo, self.out)

    def test_symlink_and_unreviewed_skill_payload_rejected(self):
        link = self.source / "assets/leak.svg"
        link.symlink_to(self.repo / "PRIVACY.md")
        with self.assertRaises(ValueError):
            builder.build(self.repo, self.out)
        link.unlink()
        (self.source / "skills/get-started/install.sh").write_text("exit 0")
        with self.assertRaises(ValueError):
            builder.build(self.repo, self.out)


if __name__ == "__main__":
    unittest.main()
