"""Resolve read/write paths for local repo vs Kaggle notebook environments."""

from __future__ import annotations

import glob
import sys
from dataclasses import dataclass
from pathlib import Path

KAGGLE_INPUT = Path("/kaggle/input")
KAGGLE_WORKING = Path("/kaggle/working")


def is_kaggle() -> bool:
    return KAGGLE_INPUT.is_dir()


def is_local_venv() -> bool:
    return (not is_kaggle()) and (".venv" in Path(sys.prefix).parts)


def _detect_local_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    for root in (cwd, cwd.parent):
        if (root / "data").is_dir() or (root / "notebooks" / "env_paths.py").is_file():
            return root
    return cwd


def _glob_dir(patterns: list[str]) -> Path | None:
    for pattern in patterns:
        for match in sorted(glob.glob(pattern, recursive=True)):
            path = Path(match)
            if path.is_dir():
                return path
    return None


def _glob_file(patterns: list[str], *, name: str | None = None) -> Path | None:
    for pattern in patterns:
        for match in sorted(glob.glob(pattern, recursive=True)):
            path = Path(match)
            if not path.is_file():
                continue
            if name is not None and path.name != name:
                continue
            return path
    return None


def _find_cg_dir(search_root: Path) -> Path | None:
    patterns = [
        str(search_root / "competitions/pokemon-tcg-ai-battle/sample_submission/cg"),
        str(search_root / "pokemon-tcg-ai-battle/sample_submission/cg"),
        str(search_root / "**/sample_submission/cg"),
        str(search_root / "**/cg-lib/cg"),
        str(search_root / "**/cg"),
    ]
    for pattern in patterns:
        for match in sorted(glob.glob(pattern, recursive=True)):
            path = Path(match)
            if path.is_dir() and (path / "api.py").exists():
                return path
    return None


def _resolve_notebooks_dir(repo_root: Path, input_root: Path | None) -> Path:
    candidates = [repo_root / "notebooks", repo_root]
    if input_root is not None:
        found = _glob_dir([str(input_root / "**/notebooks")])
        if found is not None:
            candidates.insert(0, found)
    for path in candidates:
        if (path / "env_paths.py").exists() or (path / "build_merged_agent.py").exists():
            return path
    return repo_root / "notebooks"


def discover_notebooks_dir() -> Path:
    """Find the folder containing env_paths.py for local or Kaggle runs."""
    candidates: list[Path] = []
    if is_kaggle():
        candidates.extend([KAGGLE_WORKING / "notebooks", KAGGLE_WORKING])
        candidates.extend(Path(p).parent for p in glob.glob(str(KAGGLE_INPUT / "**/env_paths.py"), recursive=True))
    else:
        cwd = Path.cwd().resolve()
        candidates.extend([cwd, cwd / "notebooks", _detect_local_repo_root() / "notebooks"])

    seen: set[str] = set()
    for path in candidates:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        if (path / "env_paths.py").exists():
            return path
    raise FileNotFoundError(
        "Could not locate notebooks/env_paths.py. "
        "Local: run from repo with notebooks/env_paths.py present. "
        "Kaggle: add this repo as an input dataset or copy notebooks/ into /kaggle/working/."
    )


def _resolve_ref_dir(repo_root: Path, input_root: Path | None) -> Path:
    candidates = [
        repo_root / "docs" / "resources" / "reference_notebooks",
    ]
    if input_root is not None:
        found = _glob_dir([str(input_root / "**/reference_notebooks")])
        if found is not None:
            candidates.insert(0, found)
    for path in candidates:
        if path.is_dir():
            return path
    return candidates[0]


@dataclass(frozen=True)
class EnvPaths:
    environment: str
    repo_root: Path
    input_root: Path | None
    output_root: Path
    data_read_dir: Path
    deck_path: Path | None
    cg_dir: Path | None
    ref_dir: Path
    notebooks_dir: Path
    main_py: Path
    merged_main_py: Path
    submission_tar: Path
    using_local_venv: bool

    def ensure_dirs(self) -> None:
        self.output_root.mkdir(parents=True, exist_ok=True)
        if self.environment == "local":
            self.data_read_dir.mkdir(parents=True, exist_ok=True)
            self.notebooks_dir.mkdir(parents=True, exist_ok=True)


def get_paths() -> EnvPaths:
    if is_kaggle():
        repo_root = KAGGLE_WORKING
        deck_path = _glob_file(
            [
                str(KAGGLE_INPUT / "**/deck.csv"),
                str(KAGGLE_INPUT / "competitions/pokemon-tcg-ai-battle/**/*.csv"),
            ],
            name="deck.csv",
        )
        cg_dir = _find_cg_dir(KAGGLE_INPUT)
        data_read = deck_path.parent if deck_path is not None else KAGGLE_INPUT
        ref_dir = _resolve_ref_dir(repo_root, KAGGLE_INPUT)
        notebooks_dir = _resolve_notebooks_dir(repo_root, KAGGLE_INPUT)

        return EnvPaths(
            environment="kaggle",
            repo_root=repo_root,
            input_root=KAGGLE_INPUT,
            output_root=KAGGLE_WORKING,
            data_read_dir=data_read,
            deck_path=deck_path,
            cg_dir=cg_dir,
            ref_dir=ref_dir,
            notebooks_dir=notebooks_dir,
            main_py=KAGGLE_WORKING / "main.py",
            merged_main_py=KAGGLE_WORKING / "merged_agent_main.py",
            submission_tar=KAGGLE_WORKING / "submission.tar.gz",
            using_local_venv=False,
        )

    repo_root = _detect_local_repo_root()
    data_read = repo_root / "data"
    deck_path = data_read / "deck.csv"
    cg_dir = data_read / "cg"

    return EnvPaths(
        environment="local",
        repo_root=repo_root,
        input_root=None,
        output_root=repo_root,
        data_read_dir=data_read,
        deck_path=deck_path if deck_path.exists() else None,
        cg_dir=cg_dir if (cg_dir / "api.py").exists() else _find_cg_dir(repo_root),
        ref_dir=_resolve_ref_dir(repo_root, None),
        notebooks_dir=repo_root / "notebooks",
        main_py=repo_root / "main.py",
        merged_main_py=repo_root / "notebooks" / "merged_agent_main.py",
        submission_tar=repo_root / "submission.tar.gz",
        using_local_venv=is_local_venv(),
    )


def stage_deck_for_build(paths: EnvPaths) -> Path:
    """Ensure deck.csv exists under output_root for packaging and main.py cwd reads."""
    if paths.deck_path is None or not paths.deck_path.exists():
        raise FileNotFoundError(
            "deck.csv not found. Local: add data/deck.csv. "
            "Kaggle: attach a dataset with deck.csv under /kaggle/input."
        )

    target = paths.output_root / "deck.csv"
    if paths.deck_path.resolve() != target.resolve():
        target.write_text(paths.deck_path.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def describe_paths(paths: EnvPaths) -> str:
    lines = [
        f"environment: {paths.environment}",
        f"repo_root: {paths.repo_root}",
        f"input_root: {paths.input_root}",
        f"output_root: {paths.output_root}",
        f"data_read_dir: {paths.data_read_dir}",
        f"deck_path: {paths.deck_path}",
        f"cg_dir: {paths.cg_dir}",
        f"ref_dir: {paths.ref_dir}",
        f"notebooks_dir: {paths.notebooks_dir}",
        f"main_py (write): {paths.main_py}",
        f"submission_tar (write): {paths.submission_tar}",
        f"using_local_venv: {paths.using_local_venv}",
    ]
    return "\n".join(lines)
