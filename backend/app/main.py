from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.lifecycle import HealthState, create_lifespan
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings)

    app = FastAPI(
        title=resolved_settings.app_name,
        summary=resolved_settings.api_summary,
        description=resolved_settings.api_description,
        version=resolved_settings.app_version,
        root_path=resolved_settings.proxy_root_path,
        openapi_url=resolved_settings.openapi_url,
        docs_url=resolved_settings.docs_url,
        redoc_url=resolved_settings.redoc_url,
        lifespan=create_lifespan(resolved_settings),
    )

    app.state.settings = resolved_settings
    app.state.health = HealthState()
    app.state.service_registry = {}

    app.add_middleware(
        RequestContextMiddleware,
        request_id_header=resolved_settings.request_id_header,
    )

    if resolved_settings.cors_allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=resolved_settings.cors_allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=resolved_settings.api_v1_prefix)
    return app


app = create_app()
