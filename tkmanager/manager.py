import os
from typing import Any, Literal, Optional, overload
from datetime import datetime
from dataclasses import InitVar, dataclass, field

import orjson as json
from cryptography.fernet import Fernet

from . import exceptions as ex


ENCODING = 'utf-8'
HOME_DIR = os.path.expanduser('~')
KEY = 'TKMANAGER_KEY'
FILE = 'TKMANAGER'
PATH = os.path.join(HOME_DIR, FILE)


@dataclass
class Token:
    t: str
    expires: datetime = field(init=False)
    expires_: InitVar[str | datetime]


    def __post_init__(self, expires_: str | datetime):
        if isinstance(expires_, str):
            expires_ = datetime.fromisoformat(expires_)
        self.expires = expires_


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


    def make_file(self) -> None:
        with open(self._file_location, 'w'):
            pass


    @overload
    def read_data(self, as_bytes: Literal[False]) -> dict[str, Any]: ...
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
        data = self.read_data(False)
        try:
            token_group = data[token_group]
        except KeyError:
            raise ex.GroupNotFoundError(f"The group '{token_group}' was not found.")
        raise NotImplementedError()


    def store_token(self, token_value: dict[str, Any], token_name: str, token_group: str = 'default') -> None:
        raise NotImplementedError()
