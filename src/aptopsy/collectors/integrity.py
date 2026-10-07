import re
import subprocess

from aptopsy.models import IntegrityIssue


VERIFY_PATTERN = re.compile(
    r"^(?P<flags>.{9}) (?P<attribute>.) (?P<path>.+)$"
)


def parse_integrity_line(line: str) -> IntegrityIssue | None:
    line = line.rstrip()

    if not line:
        return None

    # dpkg reports missing files using:
    #
    # missing [c] pathname [(error-message)]
    #
    if line.startswith("missing "):
        remainder = line[len("missing "):]

        is_config = False

        if remainder.startswith("c "):
            is_config = True
            remainder = remainder[2:]

        error = None
        path = remainder

        # A missing entry may end in:
        #
        # (error-message)
        #
        if " (" in remainder and remainder.endswith(")"):
            path, error_part = remainder.rsplit(" (", 1)
            error = error_part[:-1]

        return IntegrityIssue(
            path=path,
            flags="missing",
            is_config=is_config,
            missing=True,
            error=error,
        )

    # Normal dpkg --verify rpm-format output:
    #
    # ?M5?????? c /etc/example.conf
    #
    match = VERIFY_PATTERN.match(line)

    if match is None:
        return IntegrityIssue(
            path=line,
            flags="unknown",
        )

    flags = match.group("flags")
    attribute = match.group("attribute")
    path = match.group("path")

    return IntegrityIssue(
        path=path,
        flags=flags,
        is_config=(attribute == "c"),
    )


def get_integrity_issues(package: str) -> list[IntegrityIssue]:
    result = subprocess.run(
        [
            "dpkg",
            "--verify",
            "--verify-format=rpm",
            package,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0 and result.stderr.strip():
        raise RuntimeError(
            f"dpkg verification failed: {result.stderr.strip()}"
        )

    issues = []

    for line in result.stdout.splitlines():
        issue = parse_integrity_line(line)

        if issue is not None:
            issues.append(issue)

    return issues
