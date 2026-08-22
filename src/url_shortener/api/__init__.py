from fastapi import APIRouter

from url_shortener.api.links import router as links_router

main_router = APIRouter()
main_router.include_router(links_router)