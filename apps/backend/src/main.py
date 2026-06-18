from fastapi import HTTPException
from fastapi import FastAPI
from sqlalchemy import text

from src.pipeline.dependencies import SessionDep
from src.pipeline.routers import router as pipeline_router

app = FastAPI()
app.include_router(pipeline_router, prefix="/pipeline", tags=["pipeline"])


@app.get("/health")
def health_check(db: SessionDep):
    """Check the health of the application and its dependencies."""

    try:
        db.execute(text("SELECT 1"))
        return {"status": "OK"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database connection failed")
