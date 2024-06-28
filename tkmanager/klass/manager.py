import os
from typing import Any, Literal, Optional, overload
from dataclasses import dataclass, field
from datetime import datetime
from time import time

import orjson as json
from cryptography.fernet import Fernet

from .. import exceptions as ex


ENCODING = 'utf-8'
HOME_DIR = os.path.expanduser('~')
KEY = 'TKMANAGER_KEY'
FILE = 'TKMANAGER'
PATH = os.path.join(HOME_DIR, FILE)


def _now() -> int:
    return int(time())


@dataclass(init=False, repr=False)
class Token:
    t: str = field(repr=False)
    expires: Optional[int]


    def __init__(self, t: str, expires: int | datetime | None = None):
        self.t = t
        if isinstance(expires, datetime):
            expires = int(expires.timestamp())
        self.expires = expires


    def __repr__(self) -> str:
        return f"Token(t=***, expires={self.expires if self.expires else None})"
    
    
    def __str__(self) -> str:
        return f"{self.t} : {self.expires}" if self.expires else self.t


    @property
    def is_expired(self) -> bool:
        if self.expires:
            return self.expires <= _now()
        return False


class Manager:
    def __init__(self, key: Optional[bytes] = None, file_location: str = PATH) -> None:
        self._key = key or self.read_key()
        self._file_location = file_location
        self._encrypter = Fernet(self._key)


    def read_key(self) -> bytes:
        decoded_key = os.getenv(KEY)
        if not decoded_key:
            raise ex.KeyNotFoundError('Please store a key in your enviroment variables.')
        return decoded_key.encode(ENCODING)


    @classmethod
    def has_key(cls) -> bool:
        return KEY in os.environ


    @classmethod
    def make_key(cls) -> str:
        return Fernet.generate_key().decode(ENCODING)


    def has_file(self) -> bool:
        return os.path.exists(self._file_location)


    def make_file(self) -> None:
        with open(self._file_location, 'wb+') as file:
            data = file.read()
            if data:
                raise ex.FileOverwriteError("There's already data in this file.")
            file.write(self._encrypter.encrypt(json.dumps({})))


    @overload
    def read_data(self, as_bytes: Literal[False] = False) -> dict[str, Any]: ...
    @overload
    def read_data(self, as_bytes: Literal[True]) -> bytes: ...

    def read_data(self, as_bytes: bool = False) -> dict[str, Any] | bytes:
        with open(self._file_location, 'rb') as file:
            encrypted_data = file.read()
        data = self._encrypter.decrypt(encrypted_data)

        if as_bytes:
            return data
        return json.loads(data)


    def store_data(self, data: dict[str, Any] | bytes) -> None:
        if isinstance(data, dict):
            data = json.dumps(data)

        encrypted_data = self._encrypter.encrypt(data)
        with open(self._file_location, 'wb') as file:
            file.write(encrypted_data)


    def read_token(self, token_name: str, token_group: str = 'default') -> Token:
        token_group = token_group.upper()
        token_name = token_name.lower()
        data = self.read_data(False)
        try:
            token_group_data: dict[str, dict[str, Any]] = data[token_group]
        except KeyError:
            raise ex.GroupNotFoundError(f"The group '{token_group}' was not found.")
        token = Token(**token_group_data[token_name])
        return token
    
    
    def read_tokens(self) -> dict[str, dict[str, Token]]:
        return {
            group: {
                token_name: Token(**token)
                for token_name, token
                in tokens.items()
            } 
            for group, tokens
            in self.read_data().items()
        }


    def store_token(
        self,
        token: Token,
        token_name: str,
        token_group: str = 'DEFAULT',
        force: bool = False
    ) -> None:
        token_group = token_group.upper()
        token_name = token_name.lower()
        data = self.read_data(False)

        data.setdefault(token_group, {})
        token_group_data: dict[str, Token] = data[token_group]

        if token_name in token_group_data and not force:
            raise ex.TokenOverwriteError(f"Token '{token_name}' is already defined in group '{token_group}'.")

        token_group_data[token_name] = token
        self.store_data(data)