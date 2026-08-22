from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import url_shortener.models # pylint: disable=unused-import
from url_shortener.api import main_router
from url_shortener.db.session import setup_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(main_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


def run() -> None:
    uvicorn.run('url_shortener.main:app', host='0.0.0.0', port=8000, reload=True)
    
if __name__ == '__main__':
    run()