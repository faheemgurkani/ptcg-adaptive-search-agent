"""Resolve read/write paths for local repo vs Kaggle notebook environments."""

from __future__ import annotations

import glob
import sys
from dataclasses import dataclass
from pathlib import Path

KAGGLE_INPUT = Path("/kaggle/input")
KAGGLE_WORKING = Path("/kaggle/working")

OFFICIAL_DIRNAME = "pokemon-tcg-ai-battle"
SAMPLE_SUBMISSION_PARTS = ("sample_submission", "sample_submission")


def is_kaggle() -> bool:
    return KAGGLE_INPUT.is_dir()


def is_local_venv() -> bool:
    return (not is_kaggle()) and (".venv" in Path(sys.prefix).parts)


def _detect_local_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    for root in [cwd, *cwd.parents]:
        if (root / "scripts" / "env_paths.py").is_file():
            return root
        if (root / "notebooks" / "ptcg-merged-agent-workbench.ipynb").is_file():
            return root
        if (root / "notebooks" / "PHASE_01_BASELINE_EVAL.ipynb").is_file():
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


def _sample_submission_dir(competition_dir: Path) -> Path:
    return competition_dir.joinpath(*SAMPLE_SUBMISSION_PARTS)


def _find_competition_dir(search_root: Path) -> Path | None:
    direct = search_root / "data" / OFFICIAL_DIRNAME
    if direct.is_dir():
        return direct

    patterns = [
        str(search_root / OFFICIAL_DIRNAME),
        str(search_root / "competitions" / OFFICIAL_DIRNAME),
        str(search_root / "**" / OFFICIAL_DIRNAME),
    ]
    return _glob_dir(patterns)


def _find_cg_dir(search_root: Path, competition_dir: Path | None = None) -> Path | None:
    candidates: list[Path] = []
    if competition_dir is not None:
        candidates.append(_sample_submission_dir(competition_dir) / "cg")
    candidates.extend(
        [
            search_root / "data" / "cg",
            search_root / "cg",
        ]
    )

    for path in candidates:
        if path.is_dir() and (path / "api.py").exists():
            return path

    patterns = [
        str(search_root / "competitions/pokemon-tcg-ai-battle/sample_submission/sample_submission/cg"),
        str(search_root / "pokemon-tcg-ai-battle/sample_submission/sample_submission/cg"),
        str(search_root / "**/sample_submission/sample_submission/cg"),
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


def _resolve_deck_path(competition_dir: Path | None, user_deck: Path) -> Path | None:
    if user_deck.exists():
        return user_deck
    if competition_dir is not None:
        sample_deck = _sample_submission_dir(competition_dir) / "deck.csv"
        if sample_deck.exists():
            return sample_deck
    return None


def _resolve_notebooks_dir(repo_root: Path, input_root: Path | None) -> Path:
    candidates = [repo_root / "notebooks", repo_root]
    if input_root is not None:
        found = _glob_dir([str(input_root / "**/notebooks")])
        if found is not None:
            candidates.insert(0, found)
    for path in candidates:
        if path.is_dir() and any(path.glob("*.ipynb")):
            return path
        if (path / "build_merged_agent.py").exists() or (path / "env_paths.py").exists():
            return path
    return repo_root / "notebooks"


def discover_notebooks_dir() -> Path:
    candidates: list[Path] = []
    if is_kaggle():
        candidates.extend([KAGGLE_WORKING / "notebooks", KAGGLE_WORKING])
        candidates.extend(
            Path(p).parent
            for p in glob.glob(str(KAGGLE_INPUT / "**/env_paths.py"), recursive=True)
        )
        candidates.extend(
            Path(p).parent
            for p in glob.glob(str(KAGGLE_INPUT / "**/ptcg-merged-agent-workbench.ipynb"), recursive=True)
        )
    else:
        cwd = Path.cwd().resolve()
        repo = _detect_local_repo_root()
        candidates.extend([cwd, cwd / "notebooks", repo / "notebooks", repo / "scripts"])

    seen: set[str] = set()
    for path in candidates:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        if path.is_dir() and any(path.glob("*.ipynb")):
            return path
        if (path / "env_paths.py").exists() and (path.parent / "notebooks").is_dir():
            return path.parent / "notebooks"
    raise FileNotFoundError(
        "Could not locate notebooks/. "
        "Local: run from repo with notebooks/ present and scripts/env_paths.py. "
        "Kaggle: add this repo as an input dataset or copy notebooks/ into /kaggle/working/."
    )


def discover_scripts_dir() -> Path:
    """Directory containing env_paths.py and other project CLI modules."""
    if is_kaggle():
        for match in sorted(glob.glob(str(KAGGLE_INPUT / "**/env_paths.py"), recursive=True)):
            return Path(match).parent
        for candidate in (KAGGLE_WORKING / "scripts", KAGGLE_WORKING):
            if (candidate / "env_paths.py").exists():
                return candidate
    repo = _detect_local_repo_root()
    scripts = repo / "scripts"
    if (scripts / "env_paths.py").exists():
        return scripts
    here = Path(__file__).resolve().parent
    if (here / "env_paths.py").exists():
        return here
    raise FileNotFoundError("Could not locate scripts/env_paths.py")


def _resolve_ref_dir(repo_root: Path, input_root: Path | None) -> Path:
    candidates = [
        repo_root / "docs" / "resources" / "reference_notebooks",
        repo_root / "data" / "extractions",
    ]
    if input_root is not None:
        found = _glob_dir([str(input_root / "**/reference_notebooks")])
        if found is not None:
            candidates.insert(0, found)
    for path in candidates:
        if path.is_dir():
            return path
    return candidates[0]


def _ptcg_engine_dir(competition_dir: Path | None) -> Path | None:
    if competition_dir is None:
        return None
    engine_root = competition_dir / "ptcg_engine"
    if not engine_root.is_dir():
        return None
    for child in sorted(engine_root.iterdir()):
        if child.is_dir() and (child / "README.md").exists():
            return child
    return engine_root if engine_root.is_dir() else None


@dataclass(frozen=True)
class EnvPaths:
    environment: str
    repo_root: Path
    input_root: Path | None
    output_root: Path
    competition_dir: Path | None
    sample_submission_dir: Path | None
    data_read_dir: Path
    user_deck_path: Path
    deck_path: Path | None
    cg_dir: Path | None
    sample_main_py: Path | None
    card_data_en: Path | None
    card_data_jp: Path | None
    ptcg_engine_dir: Path | None
    ref_dir: Path
    notebooks_dir: Path
    main_py: Path
    merged_main_py: Path
    submission_tar: Path
    using_local_venv: bool

    def ensure_dirs(self) -> None:
        self.output_root.mkdir(parents=True, exist_ok=True)
        if self.environment == "local":
            self.user_deck_path.parent.mkdir(parents=True, exist_ok=True)
            self.notebooks_dir.mkdir(parents=True, exist_ok=True)


def get_paths() -> EnvPaths:
    if is_kaggle():
        repo_root = KAGGLE_WORKING
        competition_dir = _find_competition_dir(KAGGLE_INPUT)
        sample_submission_dir = (
            _sample_submission_dir(competition_dir) if competition_dir is not None else None
        )
        user_deck = _glob_file([str(KAGGLE_INPUT / "**/deck.csv")], name="deck.csv")
        if user_deck is None and sample_submission_dir is not None:
            user_deck = sample_submission_dir / "deck.csv"
        deck_path = user_deck if user_deck is not None and user_deck.exists() else None
        cg_dir = _find_cg_dir(KAGGLE_INPUT, competition_dir)
        data_read = competition_dir or KAGGLE_INPUT

        return EnvPaths(
            environment="kaggle",
            repo_root=repo_root,
            input_root=KAGGLE_INPUT,
            output_root=KAGGLE_WORKING,
            competition_dir=competition_dir,
            sample_submission_dir=sample_submission_dir,
            data_read_dir=data_read,
            user_deck_path=KAGGLE_WORKING / "deck.csv",
            deck_path=deck_path,
            cg_dir=cg_dir,
            sample_main_py=(sample_submission_dir / "main.py") if sample_submission_dir else None,
            card_data_en=(competition_dir / "EN_Card_Data.csv") if competition_dir else None,
            card_data_jp=(competition_dir / "JP_Card_Data.csv") if competition_dir else None,
            ptcg_engine_dir=_ptcg_engine_dir(competition_dir),
            ref_dir=_resolve_ref_dir(repo_root, KAGGLE_INPUT),
            notebooks_dir=_resolve_notebooks_dir(repo_root, KAGGLE_INPUT),
            main_py=KAGGLE_WORKING / "main.py",
            merged_main_py=KAGGLE_WORKING / "merged_agent_main.py",
            submission_tar=KAGGLE_WORKING / "submission.tar.gz",
            using_local_venv=False,
        )

    repo_root = _detect_local_repo_root()
    competition_dir = _find_competition_dir(repo_root)
    sample_submission_dir = (
        _sample_submission_dir(competition_dir) if competition_dir is not None else None
    )
    user_deck = repo_root / "data" / "deck.csv"
    deck_path = _resolve_deck_path(competition_dir, user_deck)
    cg_dir = _find_cg_dir(repo_root, competition_dir)

    return EnvPaths(
        environment="local",
        repo_root=repo_root,
        input_root=None,
        output_root=repo_root,
        competition_dir=competition_dir,
        sample_submission_dir=sample_submission_dir,
        data_read_dir=competition_dir or (repo_root / "data"),
        user_deck_path=user_deck,
        deck_path=deck_path,
        cg_dir=cg_dir,
        sample_main_py=(sample_submission_dir / "main.py") if sample_submission_dir else None,
        card_data_en=(competition_dir / "EN_Card_Data.csv") if competition_dir else None,
        card_data_jp=(competition_dir / "JP_Card_Data.csv") if competition_dir else None,
        ptcg_engine_dir=_ptcg_engine_dir(competition_dir),
        ref_dir=_resolve_ref_dir(repo_root, None),
        notebooks_dir=repo_root / "notebooks",
        main_py=repo_root / "main.py",
        merged_main_py=repo_root / "notebooks" / "merged_agent_main.py",
        submission_tar=repo_root / "submission.tar.gz",
        using_local_venv=is_local_venv(),
    )


def setup_runtime(paths: EnvPaths) -> None:
    """Add the official cg SDK to sys.path for local/Kaggle notebook testing."""
    if paths.cg_dir is None or not paths.cg_dir.exists():
        raise FileNotFoundError(
            "cg SDK not found. Expected local path: "
            "data/pokemon-tcg-ai-battle/sample_submission/sample_submission/cg"
        )
    cg_parent = str(paths.cg_dir.parent)
    if cg_parent not in sys.path:
        sys.path.insert(0, cg_parent)


def stage_deck_for_build(paths: EnvPaths) -> Path:
    """Copy the active deck into output_root/deck.csv for packaging."""
    if paths.deck_path is None or not paths.deck_path.exists():
        raise FileNotFoundError(
            "deck.csv not found. Local options: data/deck.csv (your deck) or the official "
            "sample at data/pokemon-tcg-ai-battle/sample_submission/sample_submission/deck.csv. "
            "Kaggle: attach competition data or a dataset with deck.csv under /kaggle/input."
        )

    target = paths.output_root / "deck.csv"
    if paths.deck_path.resolve() != target.resolve():
        target.write_text(paths.deck_path.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def official_data_status(paths: EnvPaths) -> list[dict[str, object]]:
    rows = [
        ("competition_dir", paths.competition_dir),
        ("sample_submission_dir", paths.sample_submission_dir),
        ("sample_main_py", paths.sample_main_py),
        ("official_sample_deck", (paths.sample_submission_dir / "deck.csv") if paths.sample_submission_dir else None),
        ("active_deck_path", paths.deck_path),
        ("user_deck_override", paths.user_deck_path),
        ("cg_dir", paths.cg_dir),
        ("card_data_en", paths.card_data_en),
        ("card_data_jp", paths.card_data_jp),
        ("ptcg_engine_dir", paths.ptcg_engine_dir),
    ]
    return [
        {"resource": name, "path": str(path) if path is not None else None, "exists": bool(path and path.exists())}
        for name, path in rows
    ]


def describe_paths(paths: EnvPaths) -> str:
    lines = [
        f"environment: {paths.environment}",
        f"repo_root: {paths.repo_root}",
        f"input_root: {paths.input_root}",
        f"output_root: {paths.output_root}",
        f"competition_dir: {paths.competition_dir}",
        f"sample_submission_dir: {paths.sample_submission_dir}",
        f"data_read_dir: {paths.data_read_dir}",
        f"user_deck_path: {paths.user_deck_path}",
        f"deck_path: {paths.deck_path}",
        f"cg_dir: {paths.cg_dir}",
        f"ptcg_engine_dir: {paths.ptcg_engine_dir}",
        f"ref_dir: {paths.ref_dir}",
        f"notebooks_dir: {paths.notebooks_dir}",
        f"main_py (write): {paths.main_py}",
        f"submission_tar (write): {paths.submission_tar}",
        f"using_local_venv: {paths.using_local_venv}",
    ]
    return "\n".join(lines)
