import os
from typing import Any, Union, Literal, overload

import orjson as json
from cryptography.fernet import Fernet


ENCODING = 'utf-8'
HOME_DIR = os.path.expanduser('~')
KEY = 'TKMANAGER_KEY'
FILE = 'TKMANAGER'
PATH = os.path.join(HOME_DIR, FILE)


Data = dict[str, Any]


class Manager:
    def __init__(self, key: bytes, file_location: str) -> None:
        self._key = key
        self._file_location = file_location
        self._encrypter = Fernet(self._key)

    @overload
    def data(self, as_bytes: Literal[True]) -> Data: ...
    @overload
    def data(self, as_bytes: Literal[False]) -> bytes: ...

    def data(self, as_bytes: bool) -> Union[Data, bytes]:
        with open(self._file_location, 'rb', encoding=ENCODING) as file:
            encrypted_data = file.read()
            data = self._encrypter.decrypt(encrypted_data)
            if as_bytes:
                return data
            return json.loads(data)
