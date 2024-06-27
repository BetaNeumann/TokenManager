from rich import print
from . import cli


if __name__ == '__main__':
    if not cli.MANAGER.has_file():
        print(
            "[red]WARNING! NO FILE FOUND!",
            "Create one with the command [bright_cyan]'tkmanager make_file'[/bright_cyan].",
            sep='\n', end=''
        )
    cli.app()
