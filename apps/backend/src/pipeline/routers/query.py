from fastapi import APIRouter, HTTPException, status

from src.pipeline.database import conn_manager
from src.pipeline.exceptions import AgentError
from src.pipeline.schemas import QueryResponse
from src.pipeline.service import generate_response

router = APIRouter()


@router.post(
    "/query",
    summary="Query the database",
    description="Ask a question in plain English and get an answer drawn directly from your data.",
    response_model=QueryResponse,
)
def query(prompt: str) -> QueryResponse:
    if not conn_manager.is_connected():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to any database.",
        )

    try:
        return generate_response(prompt)
    except AgentError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your query. Please try again.",
        )
