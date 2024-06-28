from typing import Optional, Any
from typing_extensions import Annotated
from datetime import datetime

import typer
from rich import print
from rich.text import Text
from rich.tree import Tree

from tkmanager import _get_name, _get_version
from . import messages as msgs, parsers as parse
from .. import exceptions as ex
from ..manager.manager import Manager, Token


app = typer.Typer(
    name=_get_name(),
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    invoke_without_command=True
)


MANAGER = Manager()


def _version(called: bool) -> None:
    if called:
        print(f"[bright_cyan]{_get_name()} v{_get_version()}")
        raise typer.Exit()


def _make_file(called: bool) -> None:
    if called:
        try:
            MANAGER.make_file()
        except ex.FileOverwriteError:
            print('[red]File already exists...')
            raise typer.Abort()
        print(f"File was {msgs.SUCCESSFULLY} created!")


@app.callback()
def main(
    version: Annotated[
        bool, typer.Option(
            '--version', '-v',
            help='Show current version of tkmanager.',
            callback=_version,
            is_eager=True
        )
    ] = False,
    make_file: Annotated[
        bool, typer.Option(
            '--make-file', '-m',
            help='Create file before execution of command.',
            callback=_make_file,
            is_eager=True
        )
    ] = False
) -> None:
    """Manages the safe storage of Tokens!"""
    if not MANAGER.has_file():
        print(
            "[red]WARNING! NO FILE FOUND!",
            "Create a new file with the command [bright_cyan]'tkmanager --make-file'[/bright_cyan].",
            sep='\n'
        )
        raise typer.Abort()


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
        Optional[int], typer.Option(
            '--expires', '-e',
            help='Define an expiration date/unix time for the token.',
            show_default=False,
            parser=parse.expiration
        )
    ] = None,
    force: Annotated[
        bool, typer.Option(
            '--force', '-f',
            help='Force token to be overwritten'
        )
    ] = False
) -> None:
    new_token = Token(token, expires)
    MANAGER.store_token(token=new_token, token_name=token_name, token_group=group, force=force)

    msg = f"The token '{token_name}' "
    if group != 'DEFAULT':
        msg += f"from the group '{group}' "
    msg += f"was {msgs.SUCCESSFULLY} stored."
    print(msg)


@app.command()
def read(
    token_name: str,
    group: Annotated[
        str, typer.Option(
            '--group', '-g',
            help='Group used to avoid name collisions.',
            show_default=False
        )
    ] = 'DEFAULT',
    expires: Annotated[
        bool, typer.Option(
            '--expires', '-e',
            help="Shows the token with it's expiration unix time.",
        )
    ] = False
) -> None:
    token = MANAGER.read_token(token_name=token_name, token_group=group)
    msg = token.t
    if expires and token.expires:
        msg += f" : {token.expires}"
    print(msg)


@app.command(name='list')
def list_(
    group: Annotated[
        Optional[str], typer.Option(
            '--group', '-g',
            help='Lists only the specified group',
            show_default=False
        )
    ] = None,
    expired_only: Annotated[
        bool, typer.Option(
            '--expired-only', '-e',
            help=''
        )
    ] = False
) -> None:
    def add_token_branches(tree: Tree, tokens: dict[str, Any]) -> None:
        for token_name, token in sorted(tokens.items()):
            token_description = f"[red]{token_name}[/red] : [bright_cyan]{token['expires']}" if token['expires']\
                                else f"[red]{token_name}"

            tree.add(token_description)

    data = MANAGER.read_data()
    if not data:
        print('No tokens stored...')
        return

    if group:
        if group not in data:
            print(f"[red]Group '{group}' NOT FOUND!")
            raise typer.Abort()

        tokens = data[group]
        tree = Tree(group, style='bold')
        add_token_branches(tree, tokens)
    else:
        tree = Tree('Tokens', hide_root=True, style='bold')
        for group, tokens in sorted(
            data.items(),
            key=lambda x: (0, '') if x == 'DEFAULT' else (1, x)
        ):
            group_tree = tree.add(group)
            add_token_branches(group_tree, tokens)
    print(tree)
