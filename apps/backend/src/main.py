from fastapi import FastAPI, HTTPException

from src.core.logging import setup_logging
from src.database import conn_manager
from src.pipeline.routers import connection, query

setup_logging()

app = FastAPI()
app.include_router(connection.router, prefix="/pipeline", tags=["pipeline"])
app.include_router(query.router, prefix="/pipeline", tags=["pipeline"])


@app.get(
    "/health",
    summary="Health check",
    description="Check the health of the application and its dependencies.",
)
def health_check() -> dict[str, str]:
    try:
        conn_manager.check_connection()
        return {"status": "OK"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unreachable.")
