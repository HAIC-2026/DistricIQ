"""Dependency-free pre-publication checks; reports locations/types, never matched values.

Checks tracked + non-ignored files (default), the staged snapshot (--staged), or
all reachable history blobs/commit messages (--history REF). --bundles also scans
frontend build output for configured private credentials. This is a guard, not a
replacement for human review or GitHub secret scanning.
"""

import argparse
import io
import re
import subprocess
from pathlib import Path
from urllib.parse import quote, urlsplit
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private key material": rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "OpenAI token pattern": rb"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}",
    "GitHub token pattern": rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})",
    "AWS access key pattern": rb"(?:AKIA|ASIA)[A-Z0-9]{16}",
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL)


def configured_secrets():
    secrets = {}
    for folder in (ROOT, ROOT / "apps/web", ROOT / "services/api"):
        for path in folder.glob(".env*"):
            if path.name.endswith((".example", ".sample", ".template")) or not path.is_file():
                continue
            for line in path.read_text().splitlines():
                if "=" not in line or line.lstrip().startswith("#"):
                    continue
                name, value = line.split("=", 1)
                value = value.strip().strip("\"'")
                if any(s in name.upper() for s in ("KEY", "PASSWORD", "TOKEN", "SECRET")) and len(value) >= 8:
                    secrets[name] = value
                if name == "DATABASE_URL":
                    password = urlsplit(value).password
                    if password and len(password) >= 8:
                        secrets["database URL password"] = password
    return secrets


def forbidden_file(path):
    name = Path(path).name
    return (
        (name.startswith(".env") and name != ".env.example")
        or name in {"id_rsa", "id_ed25519", "credentials.json", ".netrc", ".npmrc"}
        or name.endswith((".pem", ".p12", ".pfx"))
    )


def check(path, content, secrets, findings, names=True):
    if names and forbidden_file(path):
        findings.add((path, "credential-bearing filename"))
    parts = [content]
    if content.startswith(b"PK\x03\x04"):
        try:
            with ZipFile(io.BytesIO(content)) as archive:
                parts.extend(archive.read(n) for n in archive.namelist() if not n.endswith("/"))
        except BadZipFile:
            findings.add((path, "unreadable ZIP archive"))
    for part in parts:
        for name, value in secrets.items():
            if any(v.encode() in part for v in (value, quote(value, safe=""))):
                findings.add((path, "configured private credential: " + name))
        for label, pattern in PATTERNS.items():
            if re.search(pattern, part):
                findings.add((path, label))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true")
    mode.add_argument("--history", metavar="REF")
    parser.add_argument("--bundles", action="store_true")
    args = parser.parse_args()
    secrets, findings, count = configured_secrets(), set(), 0
    if args.history:
        seen = set()
        for commit in git("rev-list", args.history).decode().splitlines():
            check("commit " + commit[:12], git("cat-file", "commit", commit), secrets, findings, names=False)
            for entry in git("ls-tree", "-rz", commit).split(b"\0"):
                if not entry:
                    continue
                metadata, path = entry.split(b"\t", 1)
                _, kind, oid = metadata.split()
                if kind != b"blob":
                    continue
                label = path.decode()
                if forbidden_file(label):
                    findings.add((label, "credential-bearing filename in history"))
                if oid not in seen:
                    check(label, git("cat-file", "blob", oid.decode()), secrets, findings)
                    seen.add(oid)
                    count += 1
    else:
        paths = git("ls-files", "-z") if args.staged else git(
            "ls-files", "--cached", "--others", "--exclude-standard", "-z"
        )
        for path in sorted(set(p.decode() for p in paths.split(b"\0") if p)):
            if args.staged:
                content = git("show", ":" + path)
            else:
                file = ROOT / path
                if not file.is_file():
                    continue
                content = file.read_bytes()
            check(path, content, secrets, findings)
            count += 1
    if args.bundles:
        for path in (ROOT / "apps/web/.next").rglob("*"):
            if path.is_file():
                # Source maps/build files may contain public paths, but private
                # credentials must never appear in any frontend build artifact.
                check(str(path.relative_to(ROOT)), path.read_bytes(), secrets, findings, names=False)
                count += 1
    print(f"Scanned {count} files/blobs; checked {len(secrets)} configured private values and known token patterns.")
    for path, kind in sorted(findings):
        print(f"BLOCKED: {path} ({kind})")
    if findings:
        print("Do not push. Investigate findings without displaying their values.")
        raise SystemExit(1)
    print("No findings. Review staged content and repository history before publishing.")


if __name__ == "__main__":
    main()
