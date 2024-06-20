from typing import Optional
from typing_extensions import Annotated

import typer
from rich import print
from cryptography.fernet import Fernet

from tkmanager import _get_name, _get_version
from . import functions as fn
from . import exceptions as ex
from . import messages as msg


app = typer.Typer(pretty_exceptions_show_locals=False)
KEY = fn.read_key()
ENCRYPTER = Fernet(KEY)


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
    return


@app.command()
def store(token_name: str, token: str, overwrite: bool = False):
    try: 
        data = fn.read_json(ENCRYPTER)
    except ex.NoTokens:
        data = {}

    if overwrite:
        confirmation = typer.prompt('Type token again for confirmation') == token_name
        if not confirmation:
            print("[red]Tokens don't match. Aborting...[/red]")
            raise typer.Exit()
    elif token_name in data and not overwrite:
        print(f"[red]Token '{token_name}' already defined. Force overwrite with --overwrite.[/red]")
        raise ex.AttemptedTokenOverwrite(3)

    data[token_name] = token
    fn.write_to_json(data, ENCRYPTER)
    print(f"Token '{token_name}' stored successfully.")


@app.command()
def retrieve(token_name: str):
    data = fn.read_json(ENCRYPTER)
    if token_name not in data:
        print(msg.TOKEN_NOT_FOUND.format(token_name))
        raise ex.TokenNotFound(2)
    print(data[token_name])


@app.command()
def delete(token_name: Annotated[str, typer.Argument()]):
    data = fn.read_json(ENCRYPTER)
    if token_name not in data:
        print(msg.TOKEN_NOT_FOUND.format(token_name))
        raise ex.TokenNotFound(2)

    confirmation = typer.prompt('Type token again for confirmation') == token_name
    if not confirmation:
        print("[red]Tokens don't match. Aborting...[/red]")
        raise typer.Exit()

    del data[token_name]
    fn.write_to_json(data, ENCRYPTER)
    print(f"Token '{token_name}' deleted successfully.")


@app.command(name='list')
def list_():
    data = fn.read_json(ENCRYPTER)
    if not data:
        print(msg.NO_TOKENS_FOUND)
        raise ex.NoTokens(1)

    for key in data:
        print(f"[green]- {key}[/green]")
