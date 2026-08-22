class AppError(Exception):
    """Base app error (not HTTP)"""
    
class LinkNotFoundError(AppError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Link not found: {code}")
        
