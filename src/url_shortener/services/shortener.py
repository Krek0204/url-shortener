"""Module contains service to generate code automatically based on entity id in database"""

import base62

class ShortenerService:
    """Service class to generate code"""
    def __init__(self):
        pass

    def create_code(self, input_id: int) -> str:
        """Creates short code with base62 encoding."""
        return base62.encode(input_id)
