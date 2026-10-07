import re
import subprocess

from aptopsy.models import RepositoryInfo


SOURCE_PATTERN = re.compile(
    r"^\s*(?P<priority>\d+)\s+"
    r"(?P<source>\S+)\s+"
    r"(?P<distribution>\S+)\s+"
    r"(?P<architecture>\S+)\s+Packages$"
)


def run_policy(package: str) -> str:
    result = subprocess.run(
        ["apt-cache", "policy", package],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or f"Could not read repository information for {package}"
        )

    return result.stdout


def get_repository_info(package: str) -> RepositoryInfo:
    output = run_policy(package)

    info = RepositoryInfo()

    lines = output.splitlines()

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("Installed:"):
            value = stripped.split(":", 1)[1].strip()

            if value != "(none)":
                info.installed = value

        elif stripped.startswith("Candidate:"):
            value = stripped.split(":", 1)[1].strip()

            if value != "(none)":
                info.candidate = value

    candidate_found = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # Examples:
        #
        # *** 5.3-3+b1 500
        #     5.3-3+b1 500

        version_line = stripped

        if version_line.startswith("***"):
            version_line = version_line[3:].strip()

        parts = version_line.split()

        if (
            len(parts) >= 2
            and info.candidate is not None
            and parts[0] == info.candidate
            and parts[1].isdigit()
        ):
            info.priority = int(parts[1])
            candidate_found = True
            continue

        if not candidate_found:
            continue

        match = SOURCE_PATTERN.match(line)

        if match is None:
            continue

        source = match.group("source")

        # Skip dpkg's local installed-status entry.
        if source.startswith("/var/lib/dpkg/"):
            continue

        info.priority = int(match.group("priority"))
        info.source = source
        info.architecture = match.group("architecture")

        distribution = match.group("distribution")

        if "/" in distribution:
            info.suite, info.component = distribution.split("/", 1)
        else:
            info.suite = distribution

        break

    return info
