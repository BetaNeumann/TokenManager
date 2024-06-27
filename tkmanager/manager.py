import os
from typing import Any, Literal, Optional, overload
from dataclasses import dataclass, field
from datetime import datetime

import orjson as json
from cryptography.fernet import Fernet

from . import exceptions as ex


ENCODING = 'utf-8'
HOME_DIR = os.path.expanduser('~')
KEY = 'TKMANAGER_KEY'
FILE = 'TKMANAGER'
PATH = os.path.join(HOME_DIR, FILE)


@dataclass(init=False, repr=False)
class Token:
    t: str = field(repr=False)
    expires: Optional[datetime]


    def __init__(self, t: str, expires: str | datetime | None = None):
        self.t = t
        if isinstance(expires, str):
            expires = datetime.fromisoformat(expires)
        self.expires = expires
    
    
    def __repr__(self) -> str:
        return f"Token(t=***, expires={self.expires.isoformat() if self.expires else None})"


    @property
    def is_expired(self) -> bool:
        if self.expires:
            return self.expires <= datetime.now()
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


    def has_key(self) -> bool:
        return KEY in os.environ


    @classmethod
    def make_key(cls) -> str:
        return Fernet.generate_key().decode(ENCODING)


    def has_file(self) -> bool:
        return os.path.exists(self._file_location)


    def make_file(self) -> None:
        with open(self._file_location, 'w+') as file:
            data = file.read()
        if data:
            raise ex.FileOverwriteError("There's already data in this file.")
        self.store_data({'DEFAULT': {}})


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
        token_group = token_name.upper()
        token_name = token_name.lower()
        data = self.read_data(False)
        try:
            token_group_data: dict[str, dict[str, Any]] = data[token_group]
        except KeyError:
            raise ex.GroupNotFoundError(f"The group '{token_group}' was not found.")
        token = Token(**token_group_data[token_name])
        return token


    def store_token(
        self,
        token: Token,
        token_name: str,
        token_group: str = 'DEFAULT',
        force: bool = False
    ) -> None:
        token_group = token_name.upper()
        token_name = token_name.lower()
        data = self.read_data(False)
        try:
            data.setdefault(token_group, {})
            token_group_data: dict[str, Token] = data[token_group]
        except KeyError:
            raise ex.GroupNotFoundError(f"The group '{token_group}' was not found.")
        
        if token_name in token_group_data and not force:
            raise ex.TokenOverwriteError(f"Token '{token_name}' is already defined in group '{token_group}'.")

        token_group_data[token_name] = token
        self.store_data(data)
