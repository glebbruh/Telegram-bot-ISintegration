from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.inspections import router as inspections_router
from app.routers.patterns import router as patterns_router
from app.routers.tasks import router as tasks_router

app = FastAPI(title="CheckOffice API")

app.include_router(auth_router)
app.include_router(inspections_router)
app.include_router(patterns_router)
app.include_router(tasks_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}