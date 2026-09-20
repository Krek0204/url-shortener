"""Main module for starting fastapi application"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from url_shortener.api import main_router
from url_shortener.config import settings
from url_shortener.errors import (
    code_already_taken_error_handler,
    code_not_found_error,
    custom_code_already_taken_error_handler,
    link_not_found_error_handler,
)
from url_shortener.exceptions import (
    CodeAlreadyTakenError,
    CodeNotFoundError,
    CustomCodeAlreadyTakenError,
    LinkNotFoundError,
)

exceptions_dict = {
    LinkNotFoundError: link_not_found_error_handler,
    CodeNotFoundError: code_not_found_error,
    CodeAlreadyTakenError: code_already_taken_error_handler,
    CustomCodeAlreadyTakenError: custom_code_already_taken_error_handler,
}

app = FastAPI(exception_handlers=exceptions_dict)

@app.get('/health', status_code=200)
def health_check():
    """API endpoint for checking application status."""
    return {"status": "ok"}

app.include_router(main_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=['*'],
    allow_headers=['*'],
)

def run() -> None:
    """Start fastapi application with uvicorn"""
    uvicorn.run('url_shortener.main:app', host='0.0.0.0', port=8000)

if __name__ == '__main__':
    run()
