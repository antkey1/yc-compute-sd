from fastapi import FastAPI

from .routes import api


def create_application() -> FastAPI:
    app = FastAPI(
        title='YC Compute Prometheus SD',
        version='0.2.0',
    )
    app.include_router(router=api.router, prefix='/api')
    return app
