from typing import Optional, Callable, Any
from typing_extensions import Annotated
from datetime import datetime

import typer
from rich import print
from rich.text import Text
from rich.tree import Tree

from tkmanager import _get_name, _get_version
from . import messages as msgs, parsers as parse
from .. import exceptions as ex
from ..klass.manager import KEY, Manager, Token


app = typer.Typer(
    name=_get_name(),
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    invoke_without_command=True
)


def _manager() -> Callable[[], Manager]:
    manager = None

    def get_manager() -> Manager:
        nonlocal manager
        if manager is None:
            manager = Manager()
        return manager

    return get_manager


def _version(called: bool) -> None:
    if called:
        print(f"[bright_cyan]{_get_name()} v{_get_version()}")
        raise typer.Exit()


def _make_file(called: bool) -> None:
    MANAGER = Manager()
    if called:
        try:
            MANAGER.make_file()
        except ex.FileOverwriteError:
            print('[red]File already exists...')
            raise typer.Abort()
        print(f"File was {msgs.SUCCESSFULLY} created!")


def _make_key(called: bool) -> None:
    if called:
        print(
            f"Save the following encryption key as the enviroment variable '{KEY}':",
            f"[bold red]{Manager.make_key()}",
            sep='\n'
        )
        raise typer.Exit()


GETTER = _manager()


@app.callback(context_settings={'obj': _manager()})
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
            '--make-file', '-mf',
            help='Create file before execution of command.',
            callback=_make_file,
            is_eager=True
        )
    ] = False,
    make_key: Annotated[
        bool, typer.Option(
            '--make-key', '-mk',
            help='Create a encryption key.',
            callback=_make_key,
            is_eager=True
        )
    ] = False
) -> None:
    """Manages the safe storage of Tokens!"""
    MANAGER = GETTER()

    should_abort = False
    msg: list[str] = []

    if not MANAGER.has_file():
        msg += [
            "[red]WARNING! NO FILE FOUND!",
            "Create a new file with the command [bright_cyan]tkmanager --make-file[/bright_cyan].\n"
        ]
        should_abort = True

    if should_abort:
        print(*msg, sep='\n')
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
    MANAGER = GETTER()

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
    MANAGER = GETTER()

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
    MANAGER = GETTER()

