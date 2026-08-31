from fastapi import Request
from fastapi.responses import JSONResponse

from url_shortener.exceptions import LinkNotFoundError, CodeAlreadyTakenError, CustomCodeAlreadyTakenError, CodeNotFoundError

def link_not_found_error_handler(request: Request, exc: LinkNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"message": f"Oops! {exc.name} did something..."}
    )
    
def code_already_taken_error_handler(request: Request, exc: CodeAlreadyTakenError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"message": f"Conflict! Error {exc.name} arrives! Code already taken..."}
    )
    
def custom_code_already_taken_error_handler(request: Request, exc: CustomCodeAlreadyTakenError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"message": f"Conflict! Error {exc.name} arrives! Code already taken..."}
    )
    
def code_not_found_error(request: Request, exc: CodeNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": f"Code not found! Error {exc.name} occurs..."}
    )