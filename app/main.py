from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api import router_v1
from app.core.config import settings
from app.db import close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_db()


main_app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
main_app.include_router(
    router_v1,
    prefix=settings.api.prefix_v1,
    tags=["v1"]
)

if __name__ == '__main__':
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
