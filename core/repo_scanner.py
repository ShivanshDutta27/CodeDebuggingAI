# core/repo_scanner.py
"""Repository Scanner and File Tree Parser for Fixie AI Debugger.

Safely traverses a local repository directory, filters out build artifacts,
extracts package manifests, and packages source files for repository-level
multi-agent analysis.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Set

CLONED_REPOS_CACHE = Path("examples/cloned_repos")

IGNORE_DIRS: Set[str] = {
    "node_modules",
    ".git",
    "__pycache__",
    "venv",
    "fixie",
    "dist",
    "build",
    ".next",
    ".cache",
    ".idea",
    ".vscode",
    "coverage",
    ".gradle",
    "target",
    "bin",
    "obj",
}

IGNORE_EXTENSIONS: Set[str] = {
    ".exe",
    ".bin",
    ".dll",
    ".so",
    ".dylib",
    ".o",
    ".a",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp4",
    ".mp3",
    ".lock",
    ".pyc",
    ".env",
}

MANIFEST_FILENAMES: Set[str] = {
    "package.json",
    "cmakelists.txt",
    "requirements.txt",
    "pyproject.toml",
    "cargo.toml",
    "pom.xml",
    "build.gradle",
    "tsconfig.json",
    "dockerfile",
    "makefile",
}

MAX_FILES_DEFAULT = 45
MAX_FILE_SIZE_DEFAULT = 60 * 1024  # 60 KB


def scan_repository(
    repo_path: str,
    max_files: int = MAX_FILES_DEFAULT,
    max_file_size: int = MAX_FILE_SIZE_DEFAULT,
) -> Dict[str, Any]:
    """Scan a repository directory and return structured metadata, tree, and contents."""
    base = Path(repo_path).resolve()
    if not base.exists() or not base.is_dir():
        raise ValueError(f"Repository path does not exist or is not a directory: {repo_path}")

    file_tree: List[Dict[str, Any]] = []
    manifest_files: Dict[str, str] = {}
    source_files: Dict[str, str] = {}

    total_scanned = 0

    for root, dirs, files in os.walk(base):
        # Exclude ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

        rel_root = Path(root).relative_to(base)

        for filename in files:
            ext = Path(filename).suffix.lower()
            if ext in IGNORE_EXTENSIONS:
                continue

            full_path = Path(root) / filename
            rel_path = str(rel_root / filename if str(rel_root) != "." else filename).replace("\\", "/")

            try:
                stat = full_path.stat()
                file_size = stat.st_size

                is_manifest = filename.lower() in MANIFEST_FILENAMES

                file_info = {
                    "path": rel_path,
                    "name": filename,
                    "extension": ext.lstrip("."),
                    "size": file_size,
                    "is_manifest": is_manifest,
                }
                file_tree.append(file_info)

                # Only read text content for candidate source files if within size limit
                if file_size <= max_file_size and total_scanned < max_files:
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                            content = f.read()

                        if is_manifest:
                            manifest_files[rel_path] = content
                        else:
                            source_files[rel_path] = content

                        total_scanned += 1
                    except Exception:
                        pass
            except Exception:
                continue

    return {
        "repo_name": base.name,
        "repo_path": str(base).replace("\\", "/"),
        "total_files": len(file_tree),
        "file_tree": file_tree,
        "manifest_files": manifest_files,
        "source_files": source_files,
    }


def is_git_url(path_or_url: str) -> bool:
    """Check if the given string is a git clone URL (HTTP, HTTPS, or SSH)."""
    if not path_or_url:
        return False
    s = path_or_url.strip()
    return (
        s.startswith("http://")
        or s.startswith("https://")
        or s.startswith("git@")
        or "github.com/" in s
        or "gitlab.com/" in s
    )


def clone_and_scan_repo(
    git_url: str,
    max_files: int = MAX_FILES_DEFAULT,
    max_file_size: int = MAX_FILE_SIZE_DEFAULT,
) -> Dict[str, Any]:
    """Shallow-clone a remote Git repository and scan its contents."""
    clean_url = git_url.strip()
    match = re.search(r"/([^/]+?)(?:\.git)?$", clean_url)
    repo_name = match.group(1) if match else "cloned_repo"

    cache_dir = CLONED_REPOS_CACHE.resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    target_dir = cache_dir / repo_name

    # If repo already cloned, do a git pull or re-clone
    if target_dir.exists():
        try:
            subprocess.run(
                ["git", "pull", "--ff-only"],
                cwd=str(target_dir),
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except Exception:
            pass
    else:
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", clean_url, str(target_dir)],
                check=True,
                capture_output=True,
                text=True,
                timeout=90,
            )
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr or e.stdout or str(e)
            raise ValueError(f"Git clone failed: {err_msg}")
        except Exception as e:
            raise ValueError(f"Failed to clone repository: {str(e)}")

    manifest = scan_repository(str(target_dir), max_files=max_files, max_file_size=max_file_size)
    manifest["repo_name"] = repo_name
    manifest["is_cloned"] = True
    manifest["remote_url"] = clean_url
    return manifest
