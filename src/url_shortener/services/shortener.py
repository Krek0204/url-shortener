import base62

class ShortenerService:
    def __init__(self):
        pass

    def create_code(self, input_id: int) -> str:
        return base62.encode(input_id)
