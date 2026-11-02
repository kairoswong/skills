"""Install plotkit into a host project, or report drift with --check."""

import argparse
import filecmp
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.join(HERE, "plotkit")


def bundle_version():
    ns = {}
    with open(os.path.join(BUNDLE, "__init__.py"), encoding="utf-8") as fh:
        text = fh.read()
    for line in text.splitlines():
        if line.startswith("__version__"):
            exec(line, ns)
    return ns.get("__version__", "unknown")


def destination(project, target):
    return os.path.join(project, target, "plotkit")


def differing_files(dest):
    diffs = []
    for dirpath, dirnames, filenames in os.walk(BUNDLE):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        rel_dir = os.path.relpath(dirpath, BUNDLE)
        for name in filenames:
            if name.endswith(".pyc"):
                continue
            rel = os.path.join(rel_dir, name) if rel_dir != "." else name
            src = os.path.join(dirpath, name)
            dst = os.path.join(dest, rel)
            if not os.path.exists(dst) or not filecmp.cmp(src, dst, shallow=False):
                diffs.append(rel)
    return diffs


def link_dir(src, dst):
    try:
        os.symlink(src, dst, target_is_directory=True)
        return "symlink"
    except (OSError, NotImplementedError):
        pass
    if os.name == "nt":
        result = subprocess.run(["cmd", "/c", "mklink", "/J", dst, src],
                                capture_output=True, text=True)
        if result.returncode == 0:
            return "junction"
    raise OSError(
        "cannot create a link (enable Developer Mode or run as admin); "
        "use --mode copy instead"
    )


def _is_link(path):
    return os.path.islink(path) or os.path.realpath(path) != os.path.abspath(path)


def remove_install(dest, force):
    if not os.path.exists(dest):
        return
    if not force:
        sys.exit(f"refusing to overwrite {dest} (use --force, or --check to inspect)")
    if _is_link(dest):
        os.rmdir(dest) if os.path.isdir(dest) else os.unlink(dest)
    elif os.path.isfile(dest):
        os.unlink(dest)
    else:
        shutil.rmtree(dest)


def install_copy(dest, force):
    remove_install(dest, force)
    shutil.copytree(BUNDLE, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def install_link(src, dest, force):
    remove_install(dest, force)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    return link_dir(src, dest)


def import_hint(project, target, dest):
    marker = os.path.join(project, target, "__init__.py")
    inside_package = os.path.exists(marker) and os.path.dirname(marker) != project
    return "src.plotkit" if inside_package else "plotkit"


def check(project, target):
    dest = destination(project, target)
    if not os.path.exists(dest):
        print(f"not installed: {dest}")
        return 1
    kind = "link" if _is_link(dest) else "copy"
    diffs = differing_files(dest)
    print(f"installed: {dest} ({kind})")
    print(f"version: bundle {bundle_version()}")
    if kind == "link":
        print("linked copy shares the bundle; no drift possible")
        return 0
    if diffs:
        print(f"drift: {len(diffs)} file(s) differ from the bundle")
        for rel in diffs[:10]:
            print(f"  {rel}")
        if len(diffs) > 10:
            print(f"  ... and {len(diffs) - 10} more")
        print("re-run with --force to refresh, or keep the local edits deliberately")
        return 1
    print("drift: none")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="host project root")
    parser.add_argument("--target", default="src",
                        help="subdirectory that receives plotkit (default: src)")
    parser.add_argument("--mode", choices=("copy", "link"), default="copy")
    parser.add_argument("--force", action="store_true", help="overwrite an existing install")
    parser.add_argument("--check", action="store_true", help="report status, change nothing")
    args = parser.parse_args()

    project = os.path.abspath(args.project)
    if args.check:
        return check(project, args.target)

    dest = destination(project, args.target)
    if args.mode == "link":
        kind = install_link(BUNDLE, dest, args.force)
        print(f"linked ({kind}) -> {dest}")
    else:
        install_copy(dest, args.force)
        print(f"copied -> {dest}")

    print(f"version: {bundle_version()}")
    print(f"import as: from {import_hint(project, args.target, dest)} import use_style")
    print("optional: scipy for statistical tests (pip install scipy)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
