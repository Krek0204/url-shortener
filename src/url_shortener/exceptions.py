class AppError(Exception):
    """Base app error (not HTTP)"""
    @property
    def name(self) -> str:
        return self.__class__.__name__

class LinkNotFoundError(AppError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Link not found: {code}")

class CodeAlreadyTakenError(AppError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"code already exists: {code}")

class CustomCodeAlreadyTakenError(CodeAlreadyTakenError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)

class CodeNotFoundError(AppError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Code not found: {code}")
