from fastapi import HTTPException
from fastapi import FastAPI
from sqlalchemy import text

from src.database import SessionDep

app = FastAPI()


@app.get("/health")
def health_check(db: SessionDep):
    """Check the health of the application and its dependencies."""

    try:
        db.execute(text("SELECT 1"))
        return {"status": "OK"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database connection failed")
