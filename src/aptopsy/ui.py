import os
import sys


def supports_color() -> bool:
    return (
        sys.stdout.isatty()
        and os.getenv("TERM") != "dumb"
        and "NO_COLOR" not in os.environ
    )


COLOR_ENABLED = supports_color()


def color(code: str, text: str) -> str:
    if not COLOR_ENABLED:
        return text

    return f"\033[{code}m{text}\033[0m"


def cyan(text: str) -> str:
    return color("96", text)


def magenta(text: str) -> str:
    return color("95", text)


def green(text: str) -> str:
    return color("92", text)


def yellow(text: str) -> str:
    return color("93", text)


def red(text: str) -> str:
    return color("91", text)


def bold(text: str) -> str:
    return color("1", text)


def dim(text: str) -> str:
    return color("2", text)


def print_banner() -> None:
    logo = r"""
 ▄▄▄       ██▓███  ▄▄▄█████▓ ▒█████   ██▓███    ██████▓██   ██▓
▒████▄    ▓██░  ██▒▓  ██▒ ▓▒▒██▒  ██▒▓██░  ██▒▒██    ▒ ▒██  ██▒
▒██  ▀█▄  ▓██░ ██▓▒▒ ▓██░ ▒░▒██░  ██▒▓██░ ██▓▒░ ▓██▄    ▒██ ██░
░██▄▄▄▄██ ▒██▄█▓▒ ▒░ ▓██▓ ░ ▒██   ██░▒██▄█▓▒ ▒  ▒   ██▒ ░ ▐██▓░
 ▓█   ▓██▒▒██▒ ░  ░  ▒██▒ ░ ░ ████▓▒░▒██▒ ░  ░▒██████▒▒ ░ ██▒▓░
 ▒▒   ▓▒█░▒▓▒░ ░  ░  ▒ ░░   ░ ▒░▒░▒░ ▒▓▒░ ░  ░▒ ▒▓▒ ▒ ░  ██▒▒▒ 
  ▒   ▒▒ ░░▒ ░         ░      ░ ▒ ▒░ ░▒ ░     ░ ░▒  ░ ░▓██ ░▒░ 
  ░   ▒   ░░         ░      ░ ░ ░ ▒  ░░       ░  ░  ░  ▒ ▒ ░░  
      ░  ░                      ░ ░                 ░  ░ ░     
                                                       ░ ░     
"""

    print(cyan(logo))
    print(dim("                 dissect your Debian system"))
    print()
    print(magenta("                    with love, by chai <3"))
    print()


def print_home() -> None:
    print_banner()

    print(bold("Usage"))
    print("  aptopsy <package>")
    print("  aptopsy --help")
    print("  aptopsy --version")

    print()
    print(bold("Example"))
    print(f"  {cyan('aptopsy')} {green('bash')}")

    print()
