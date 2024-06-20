import os
import json
import subprocess
from typing import Any

from cryptography.fernet import Fernet

from . import exceptions as ex


HOME_DIR = os.path.expanduser('~')
ENCODING = 'utf-8'
KEY = 'TKMANAGER_KEY'
JSON = 'TKMANAGER'
PATH = os.path.join(HOME_DIR, JSON)


def make_key() -> bool:
    "Creates fernet key, decodes it to a string and stores it in an envar"

    if os.getenv(KEY) is not None:
        return False

    key = Fernet.generate_key()
    decoded_key = key.decode(ENCODING)

    if os.name == 'posix':
        with open(os.path.join(HOME_DIR, '.bashrc'), 'a') as envar_file:
            envar_file.write(f'export {KEY}="{decoded_key}"\n')
        subprocess.run('source ~/.bashrc', shell=True)
    elif os.name == 'nt':
        subprocess.run(f'setx {KEY} "{decoded_key}"', shell=True)
    os.environ[KEY] = decoded_key
    return True


def read_key() -> bytes:
    "Gets the fernet key string from the envars and stores it "

    decoded_key = os.getenv(KEY)

    if decoded_key is None:
        raise ValueError('Key was not stored, maybe you need to restart your PC?')

    key = decoded_key.encode(ENCODING)
    return key


def write_to_json(data: dict[str, Any], encrypter: Fernet) -> None:
    "Converts json data to bytes and encrypts the data, then writes it to file"

    with open(PATH, 'wb') as json_file:
        json_data = json.dumps(data).encode(ENCODING)
        encrypted_json_data = encrypter.encrypt(json_data)
        json_file.write(encrypted_json_data)


def read_json(encrypter: Fernet) -> dict[str, Any]:
    "Reads bytes from file, decrypts it and returns the data as a dict"

    try:
        with open(PATH, 'rb') as json_file:
            encrypted_json_data = json_file.read()
            json_data = encrypter.decrypt(encrypted_json_data)
            return json.loads(json_data)
    except FileNotFoundError:
        raise ex.NoTokens(1)
