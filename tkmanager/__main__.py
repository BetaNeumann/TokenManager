import os
from rich import print
from . import _get_name, cli, functions as fn


def main() -> None:
    key_created = fn.make_key()
    if key_created:
        print(
            "[bold red]ATTENTION![/bold red] Restarting your machine",
            "so that your envar key is saved is [bold red]NECESSARY![/bold red]"
        )
    cli.app(prog_name=_get_name())


if __name__ == '__main__':
    main()
