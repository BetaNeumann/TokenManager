from typing import Optional, Any
from typing_extensions import Annotated
from datetime import datetime

import typer
from rich import print
from cryptography.fernet import Fernet

from tkmanager import _get_name, _get_version

app = typer.Typer(
    name=_get_name(),
    no_args_is_help=True,
    pretty_exceptions_show_locals=False
)


def _version(called: bool) -> None:
    if called:
        print(f"[bright_cyan]{_get_name()} v{_get_version()}[/bright_cyan]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        '--version',
        '-v',
        help='Show current version of tkmanager.',
        callback=_version,
        is_eager=True
    )
) -> None:
    """Manages the safe storage of Tokens!"""
