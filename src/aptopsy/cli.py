import argparse

from aptopsy.collectors.package import (
    collect_package,
    package_exists,
)

from aptopsy.ui import (
    bold,
    cyan,
    green,
    magenta,
    red,
    yellow,
    cream,
    blue,
    dim,
    print_home,
)

from aptopsy.collectors.repository import get_repository_info
from aptopsy.collectors.why import collect_why

def print_field(label: str, value: str, width: int = 14) -> None:
    print(f"  {label:<{width}}{value}")

def format_size(kb: int | None) -> str:
    if kb is None:
        return "unknown"

    if kb < 1024:
        return f"{kb} KB"

    return f"{kb / 1024:.1f} MB"


def print_package(info) -> None:
    print()
    print(f"{blue(info.name)} {dim('@')} {cyan('APTOPSY')}")
    print("─" * 24)

    print()
    print(f"{cream('Package')}")
    print(f"  Name          {info.name}")
    print(f"  Version       {info.version}")
    print(f"  Architecture  {info.architecture}")
    print(f"  Status        {info.status}")

    install_type = (
        "manual"
        if info.manually_installed
        else "automatic"
    )

    print(f"  Installed     {install_type}")
    print(f"  Size          {format_size(info.installed_size_kb)}")

    print()
    print(f"{cream('Dependencies')}")

    if info.dependencies:
        for dependency in info.dependencies:
            print(f"  {dependency}")
    else:
        print("  none")

    print()
    print(f"{cream('Required by')}")

    if info.reverse_dependencies:
        for dependency in info.reverse_dependencies:
            print(f"  {dependency}")
    else:
        print("  none")

    print()
    print(f"{cream('Configuration files')}")

    if info.config_files:
        for path in info.config_files:
            print(f"  {path}")
    else:
        print("  none")

    print()
    print(f"{cream('Integrity')}")

    if not info.integrity_issues:
        print(f"  {green('✓')} No differences reported by dpkg")
    else:
        for issue in info.integrity_issues:
            config_marker = " [config]" if issue.is_config else ""

            if issue.missing:
                print(
                    f"  {red('✗ MISSING')}   {issue.path}"
                    f"{config_marker}"
                )

                if issue.error:
                    print(f"              {issue.error}")

            elif issue.content_changed:
                print(
                    f"  {yellow('! MODIFIED')}  {issue.path}"
                    f"{config_marker}"
                )

            elif issue.mode_check_failed:
                print(
                    f"  ! MODE/TYPE {issue.path}"
                    f"{config_marker}"
                )

            else:
                print(
                    f"  ! CHANGED   {issue.path}"
                    f" [{issue.flags}]"
                    f"{config_marker}"
                )

        count = len(info.integrity_issues)

        word = (
            "discrepancy"
            if count == 1
            else "discrepancies"
        )

        print()
        print(f"  {count} integrity {word} detected")

    print()
    print(cream("Files"))
    print(f"  {len(info.files)} installed files")

def print_repo(info) -> None:
    print()
    print(cream("Repository"))

    print(
        f"  Installed       "
        f"{info.installed or 'unknown'}"
    )

    print(
        f"  Candidate       "
        f"{info.candidate or 'unknown'}"
    )

    print(
        f"  Priority        "
        f"{info.priority if info.priority is not None else 'unknown'}"
    )

    print(
        f"  Suite         "
        f"{info.suite or 'unknown'}"
    )

    print(
        f"  Component     "
        f"{info.component or 'unknown'}"
    )

    print(
        f"  Architecture  "
        f"{info.architecture or 'unknown'}"
    )

    print(
        f"  Source        "
        f"{info.source or 'local / unknown'}"
    )

def print_why(info) -> None:
    print()
    print(cream("Why"))

    if info.install_type == "manual":
        print_field("Mark", green("manual"))
        print_field(
            "Reason",
            "explicitly installed or marked manual",
        )

    elif info.install_type == "automatic":
        print_field("Mark", yellow("automatic"))
        print_field(
            "Reason",
            "installed as a dependency",
        )

    else:
        print_field("Mark", "unknown")
        print_field(
            "Reason",
            "APT installation state unavailable",
        )

    print_field(
        "First seen",
        info.install_date or "not available in dpkg logs",
    )

    if info.install_type == "manual":
        print()
        print(
            f"{green('→')} APT currently treats this package "
            "as explicitly installed."
        )

    elif info.manual_paths:
        print()
        print(cream("Dependency path"))

        for index, path in enumerate(info.manual_paths):
            if index > 0:
                print()

            for depth, package in enumerate(path):
                indent = "    " + ("    " * depth)

                if depth == 0:
                    print(f"    {package}")
                elif depth == len(path) - 1:
                    print(
                        f"{indent}└── {package} "
                        f"{green('[manual]')}"
                    )
                else:
                    print(
                        f"{indent}└── {package}"
                    )

    elif info.install_type == "automatic":
        print()
        print(
            f"  {yellow('!')} No path to a manually installed "
            "package was found."
        )

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aptopsy",
        description="Dissect Debian packages and explain their system impact.",
    )

    parser.add_argument(
        "package",
        nargs="?",
        help="package to inspect",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="aptopsy 0.1.0",
    )

    parser.add_argument(
        "--repo",
        action="store_true",
        help="show repository and candidate version info",
    )

    parser.add_argument(
        "--why",
        action="store_true",
        help="explain why a package is installed",
    )

    args = parser.parse_args()

    if args.package is None:
        print_home()
        return

    if not package_exists(args.package):
        parser.error(
            f"'{args.package}' is not installed."
        )

    try:
        info = collect_package(args.package)
    except RuntimeError as error:
        parser.error(str(error))

    print_package(info)

    if args.repo:
        try:
            repo = get_repository_info(args.package)
        except RuntimeError as error:
            parser.error(str(error))

        print_repo(repo)

    if args.why:
        why = collect_why(args.package)
        print_why(why)

if __name__ == "__main__":
    main()
