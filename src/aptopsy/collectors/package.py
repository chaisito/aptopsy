import subprocess

from aptopsy.models import PackageInfo
from aptopsy.collectors.integrity import get_integrity_issues

def run_command(*args: str) -> str:
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
    )

    return result.stdout.strip()


def package_exists(package: str) -> bool:
    result = subprocess.run(
        ["dpkg-query", "-W", package],
        capture_output=True,
        text=True,
        check=False,
    )

    return result.returncode == 0


def get_basic_info(package: str) -> PackageInfo:
    format_string = (
        "${Package}\n"
        "${Version}\n"
        "${Architecture}\n"
        "${db:Status-Status}\n"
        "${Installed-Size}\n"
    )

    output = run_command(
        "dpkg-query",
        "-W",
        f"-f={format_string}",
        package,
    )

    lines = output.splitlines()

    if len(lines) < 5:
        raise RuntimeError(f"Could not read package information for {package}")

    try:
        size = int(lines[4])
    except ValueError:
        size = None

    return PackageInfo(
        name=lines[0],
        version=lines[1],
        architecture=lines[2],
        status=lines[3],
        installed_size_kb=size,
    )


def get_manual_status(package: str) -> bool:
    manual_packages = run_command(
        "apt-mark",
        "showmanual",
    ).splitlines()

    return package in manual_packages


def get_dependencies(package: str) -> list[str]:
    output = run_command(
        "apt-cache",
        "depends",
        package,
    )

    dependencies = []

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("Depends:"):
            dependency = line.split(":", 1)[1].strip()
            dependencies.append(dependency)

    return dependencies


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

        if line and not line.startswith("Reverse Depends:"):
            dependencies.append(line)

    return sorted(set(dependencies))


def get_files(package: str) -> list[str]:
    output = run_command(
        "dpkg-query",
        "-L",
        package,
    )

    return [
        line
        for line in output.splitlines()
        if line
    ]


def get_config_files(package: str) -> list[str]:
    output = run_command(
        "dpkg-query",
        "-W",
        "-f=${Conffiles}",
        package,
    )

    config_files = []

    for line in output.splitlines():
        line = line.strip()

        if not line:
            continue

        path = line.split()[0]
        config_files.append(path)

    return config_files


def collect_package(package: str) -> PackageInfo:
    info = get_basic_info(package)

    info.manually_installed = get_manual_status(package)
    info.dependencies = get_dependencies(package)
    info.reverse_dependencies = get_reverse_dependencies(package)
    info.files = get_files(package)
    info.config_files = get_config_files(package)
    info.integrity_issues = get_integrity_issues(package)

    return info
