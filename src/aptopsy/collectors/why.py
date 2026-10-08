import gzip
import subprocess
from collections import deque
from pathlib import Path

from aptopsy.models import WhyInfo


DPKG_LOG_DIR = Path("/var/log")


def run_command(*args: str) -> str:
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
    )

    return result.stdout.strip()


def is_manual(package: str) -> bool:
    output = run_command(
        "apt-mark",
        "showmanual",
        package,
    )

    return package in output.splitlines()


def is_auto(package: str) -> bool:
    output = run_command(
        "apt-mark",
        "showauto",
        package,
    )

    return package in output.splitlines()


def get_reverse_dependencies(package: str) -> list[str]:
    output = run_command(
        "apt-cache",
        "rdepends",
        "--installed",
        package,
    )

    dependencies = []

    for line in output.splitlines()[2:]:
        line = line.strip()

        if not line:
            continue

        if line.startswith("Reverse Depends:"):
            continue

        # apt-cache may decorate some dependency output.
        line = line.strip("<>")

        if line:
            dependencies.append(line)

    return sorted(set(dependencies))


def read_log(path: Path) -> list[str]:
    try:
        if path.suffix == ".gz":
            with gzip.open(
                path,
                "rt",
                encoding="utf-8",
                errors="replace",
            ) as file:
                return file.readlines()

        return path.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

    except (OSError, PermissionError):
        return []


def get_dpkg_logs() -> list[Path]:
    logs = []

    current = DPKG_LOG_DIR / "dpkg.log"

    if current.exists():
        logs.append(current)

    rotated = sorted(
        DPKG_LOG_DIR.glob("dpkg.log.*"),
        reverse=True,
    )

    logs.extend(rotated)

    return logs


def normalize_dpkg_package(package: str) -> str:
    # dpkg logs can contain:
    #
    # libc6:amd64
    #
    # while APTOSY may receive:
    #
    # libc6

    return package.split(":", 1)[0]


def get_first_install_date(package: str) -> str | None:
    matches = []

    for log in get_dpkg_logs():
        for line in read_log(log):
            parts = line.split()

            if len(parts) < 6:
                continue

            date = parts[0]
            time = parts[1]
            action = parts[2]
            logged_package = parts[3]

            if action != "install":
                continue

            if normalize_dpkg_package(logged_package) != package:
                continue

            matches.append(f"{date} {time}")

    if not matches:
        return None

    return min(matches)


def find_manual_paths(
    package: str,
    max_depth: int = 8,
    max_paths: int = 5,
) -> list[list[str]]:
    """
    Follow reverse dependencies until we reach packages marked
    as manually installed.

    Example:

        libfoo
          <- foo-runtime
          <- foo

    becomes:

        ["libfoo", "foo-runtime", "foo"]
    """

    paths = []

    queue = deque(
        [
            (package, [package]),
        ]
    )

    # Keep track of package/depth combinations rather than blindly
    # traversing dependency cycles forever.
    visited = {(package, 0)}

    while queue and len(paths) < max_paths:
        current, path = queue.popleft()

        depth = len(path) - 1

        if depth >= max_depth:
            continue

        parents = get_reverse_dependencies(current)

        for parent in parents:
            if parent in path:
                continue

            new_path = path + [parent]

            if is_manual(parent):
                paths.append(new_path)

                if len(paths) >= max_paths:
                    break

                continue

            state = (parent, depth + 1)

            if state in visited:
                continue

            visited.add(state)
            queue.append(
                (
                    parent,
                    new_path,
                )
            )

    return paths


def collect_why(package: str) -> WhyInfo:
    manual = is_manual(package)
    automatic = is_auto(package)

    if manual:
        install_type = "manual"
    elif automatic:
        install_type = "automatic"
    else:
        install_type = "unknown"

    required_by = get_reverse_dependencies(package)

    manual_paths = []

    if automatic:
        manual_paths = find_manual_paths(package)

    return WhyInfo(
        package=package,
        install_type=install_type,
        install_date=get_first_install_date(package),
        required_by=required_by,
        manual_paths=manual_paths,
    )
