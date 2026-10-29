#!/usr/bin/env python3
"""Compare two generated output directories for byte-level reproducibility."""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python scripts/verify_reproducibility.py DIR_A DIR_B")
        return 2
    left, right = (Path(arg) for arg in sys.argv[1:])
    if not left.is_dir() or not right.is_dir():
        print("Both arguments must be existing directories.")
        return 2
    a = {p.name: p for p in left.iterdir() if p.is_file()}
    b = {p.name: p for p in right.iterdir() if p.is_file()}
    if a.keys() != b.keys():
        print("FAIL: file sets differ")
        print("Only in first:", sorted(a.keys() - b.keys()))
        print("Only in second:", sorted(b.keys() - a.keys()))
        return 1
    differences = [name for name in sorted(a) if sha256(a[name]) != sha256(b[name])]
    if differences:
        print("FAIL: checksums differ for:", ", ".join(differences))
        return 1
    print(f"PASS: {len(a)} files match byte-for-byte.")
    for name in sorted(a):
        print(f"{sha256(a[name])}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
