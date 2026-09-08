from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import url_shortener.models # pylint: disable=unused-import
from url_shortener.api import main_router
from url_shortener.errors import link_not_found_error_handler, code_already_taken_error_handler
from url_shortener.errors import custom_code_already_taken_error_handler, code_not_found_error
from url_shortener.exceptions import LinkNotFoundError, CodeNotFoundError, CodeAlreadyTakenError, CustomCodeAlreadyTakenError
from url_shortener.config import settings


app = FastAPI()

@app.get('/health', status_code=200)
def health_check():
    return {"status": "ok"}

app.include_router(main_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_exception_handler(LinkNotFoundError, link_not_found_error_handler)
app.add_exception_handler(CodeNotFoundError, code_not_found_error)
app.add_exception_handler(CodeAlreadyTakenError, code_already_taken_error_handler)
app.add_exception_handler(CustomCodeAlreadyTakenError, custom_code_already_taken_error_handler)


def run() -> None:
    uvicorn.run('url_shortener.main:app', host='0.0.0.0', port=8000)
    
if __name__ == '__main__':
    run()