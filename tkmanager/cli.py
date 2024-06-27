from typing import Optional
from typing_extensions import Annotated
from datetime import datetime

import typer
from rich import print
from rich.text import Text
from rich.tree import Tree

from tkmanager import _get_name, _get_version
from .manager import Manager, Token
from . import exceptions as ex, messages as msgs


app = typer.Typer(
    name=_get_name(),
    no_args_is_help=True,
    pretty_exceptions_show_locals=False
)


MANAGER = Manager()


def _version(called: bool) -> None:
    if called:
        print(f"[bright_cyan]{_get_name()} v{_get_version()}")
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


@app.callback()
def make_file() -> None:
    try:
        MANAGER.make_file()
    except ex.FileOverwriteError:
        print('[red]File already exists...')
        return


@app.command()
def store(
    token_name: str,
    token: str,
    group: Annotated[
        str, typer.Option(
            '--group', '-g',
            help='Group used to avoid name collisions.',
            show_default=False
        )
    ] = 'DEFAULT',
    expires: Annotated[
        Optional[datetime], typer.Option(
            '--expires', '-e',
            help='Define an expiration date for the token.',
            show_default=False
        )
    ] = None
):
    new_token = Token(token, expires)
    MANAGER.store_token(new_token, token_name, group)

    msg = f"The token '{token_name}' "
    if group != 'DEFAULT':
        msg += f"from the group '{group}' "
    msg += f"was {msgs.SUCCESSFULLY} stored."
    print(msg)


@app.command(name='list')
def list_() -> None:
    data = MANAGER.read_data(False)
    if data == {'DEFAULT': {}}:
        print('No tokens stored...')
        return

    tree = Tree('Tokens', hide_root=True, style='bold')
    for group, tokens in sorted(
        data.items(),
        key=lambda x: (0, '') if x == 'DEFAULT' else (1, x)
    ):
        group_tree = tree.add(group)
        for token_name, token in sorted(tokens.items()):
            token_description = f"{token_name}: {token['expires']}"
            group_tree.add(Text(token_description, 'red'))

    print(tree)
