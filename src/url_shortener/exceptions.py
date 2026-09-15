"""
Module specified exceptions for this application
"""

class AppError(Exception):
    """Base app error (not HTTP)"""
    @property
    def name(self) -> str:
        """Get name of this class"""
        return self.__class__.__name__

class LinkNotFoundError(AppError):
    """Error for case, when link wasn't found in database"""
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Link not found: {code}")

class CodeAlreadyTakenError(AppError):
    """
    Error for case, when automatically generated code already
    exists in database
    """
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"code already exists: {code}")

class CustomCodeAlreadyTakenError(CodeAlreadyTakenError):
    """
    Error for case, when custom code, that user want to use, already
    exists in database
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)

class CodeNotFoundError(AppError):
    """
    Error for case, when code, using to find long_url, won't found in database.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Code not found: {code}")
