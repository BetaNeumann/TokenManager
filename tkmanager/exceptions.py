from typer import Exit

class AttemptedTokenOverwrite(Exit):
    "Raised when an existing token would be overwritten by action"

class NoTokens(Exit):
    "Raised when no tokens were ever stored"

class TokenNotFound(Exit):
    "Raised when token was not found"
