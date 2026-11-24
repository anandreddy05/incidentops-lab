import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request

from incidentops_lab_api.api.routes.auth import router as auth_router
from incidentops_lab_api.api.routes.health import router as health_router
from incidentops_lab_api.api.routes.incidents import router as incidents_router
from incidentops_lab_api.api.routes.products import (
    router as products_router,
)
from incidentops_lab_api.core.config import get_settings
from incidentops_lab_api.core.context import request_id_ctx
from incidentops_lab_api.core.logging import configure_logging

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
settings = get_settings()
configure_logging(settings.log_level)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.app_name,
    description="Fault-injectable e-commerce application for IncidentOps.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(incidents_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")

@app.middleware("http")
async def request_context_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())

    token = request_id_ctx.set(request_id)

    try:
        logger.info(
            "Request received: %s %s",
            request.method,
            request.url.path,
        )

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "Request completed: %s",
            response.status_code,
        )

        return response

    finally:
        request_id_ctx.reset(token)


app.include_router(health_router)
