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
    print_home,
)

from aptopsy.collectors.repository import get_repository_info

def format_size(kb: int | None) -> str:
    if kb is None:
        return "unknown"

    if kb < 1024:
        return f"{kb} KB"

    return f"{kb / 1024:.1f} MB"


def print_package(info) -> None:
    print()
    print(f"{cyan('APTOPSY')} - {bold(info.name)}")
    print("─" * 48)

    print()
    print(f"{bold('Package')}")
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
    print(f"{bold('Dependencies')}")

    if info.dependencies:
        for dependency in info.dependencies:
            print(f"  {dependency}")
    else:
        print("  none")

    print()
    print(f"{bold('Reverse dependencies')}")

    if info.reverse_dependencies:
        for dependency in info.reverse_dependencies:
            print(f"  {dependency}")
    else:
        print("  none")

    print()
    print(f"{bold('Configuration files')}")

    if info.config_files:
        for path in info.config_files:
            print(f"  {path}")
    else:
        print("  none")

    print()
    print(f"{bold('Integrity')}")

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
    print("Files")
    print(f"  {len(info.files)} installed files")

    print()

def print_repo(info) -> None:
    print()
    print(bold("Repository"))

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

if __name__ == "__main__":
    main()
