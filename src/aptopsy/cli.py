import argparse

from aptopsy.collectors.package import (
    collect_package,
    package_exists,
)


def format_size(kb: int | None) -> str:
    if kb is None:
        return "unknown"

    if kb < 1024:
        return f"{kb} KB"

    return f"{kb / 1024:.1f} MB"


def print_package(info) -> None:
    print()
    print(f"APTOSY — {info.name}")
    print("─" * 48)

    print()
    print("Package")
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
    print("Dependencies")

    if info.dependencies:
        for dependency in info.dependencies:
            print(f"  {dependency}")
    else:
        print("  none")

    print()
    print("Reverse dependencies")

    if info.reverse_dependencies:
        for dependency in info.reverse_dependencies:
            print(f"  {dependency}")
    else:
        print("  none")

    print()
    print("Configuration files")

    if info.config_files:
        for path in info.config_files:
            print(f"  {path}")
    else:
        print("  none")

    print()
    print("Integrity")

    if not info.integrity_issues:
        print("  ✓ No differences reported by dpkg")
    else:
        for issue in info.integrity_issues:
            config_marker = " [config]" if issue.is_config else ""

            if issue.missing:
                print(
                    f"  ✗ MISSING   {issue.path}"
                    f"{config_marker}"
                )

                if issue.error:
                    print(f"              {issue.error}")

            elif issue.content_changed:
                print(
                    f"  ! MODIFIED  {issue.path}"
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


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aptopsy",
        description="Dissect Debian packages and explain their system impact.",
    )

    parser.add_argument(
        "package",
        help="package to inspect",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="aptopsy 0.1.0",
    )

    args = parser.parse_args()

    if not package_exists(args.package):
        parser.error(
            f"'{args.package}' is not installed."
        )

    try:
        info = collect_package(args.package)
    except RuntimeError as error:
        parser.error(str(error))

    print_package(info)


if __name__ == "__main__":
    main()
