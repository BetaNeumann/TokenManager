
class KeyNotFoundError(Exception):
    """Raised when a key is not found stored in the enviroment variables."""

class GroupNotFoundError(Exception):
    """Raised when a token group is not found"""

class TokenNotFoundError(Exception):
    """Raised when a token is not found within a group"""
