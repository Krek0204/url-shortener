"""
Module specified handlers, that uses to catch application exceptions
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from url_shortener.exceptions import (
    CodeAlreadyTakenError,
    CodeNotFoundError,
    CustomCodeAlreadyTakenError,
    LinkNotFoundError,
)


def link_not_found_error_handler(request: Request, exc: LinkNotFoundError) -> JSONResponse:
    """Handler for LinkNotFoundError exc. Returns 404 code"""
    return JSONResponse(
        status_code=404,
        content={"message": "Not found",
                 "detail": "No link found for the given short code.",
                 "code": exc.code
                 }
    )

def code_already_taken_error_handler(request: Request, exc: CodeAlreadyTakenError) -> JSONResponse:
    """Handler for CodeAlreadyTaken exc. Returns 500 code"""
    return JSONResponse(
        status_code=500,
        content={"message": "Conflict",
                 "detail": "Automate generated code already in use. Internal Error.",
                 "code": exc.code
                 }
    )

def custom_code_already_taken_error_handler(request: Request, exc: CustomCodeAlreadyTakenError) -> JSONResponse:
    """Handler for CustomCodeAlreadyTaken exc. Returns 409 code"""

    return JSONResponse(
        status_code=409,
        content={"message": "Conflict",
                 "detail": "This custom short code is already in use.",
                 "code": exc.code
                 }
    )

def code_not_found_error(request: Request, exc: CodeNotFoundError) -> JSONResponse:
    """Handler for CodeNotFoundError exc. Returns 500 code"""

    return JSONResponse(
        status_code=500,
        content={"message": "Internal error",
                 "detail": "Expected short code was not found after create.",
                 "code": exc.code
                 }
    )