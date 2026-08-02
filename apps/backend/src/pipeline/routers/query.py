# ruff: noqa: ANN201
from fastapi import APIRouter, HTTPException, status

from src.auth.dependencies import OptionalUser
from src.pipeline.agent.executor import generate_response
from src.pipeline.exceptions import AgentError, ConnectionNotFoundError
from src.pipeline.schemas import QueryResponse

router = APIRouter()


@router.post(
    "/query",
    summary="Query the database",
    description="Ask a question in plain English and get an answer drawn directly from your data.",
    response_model=QueryResponse,
)
def query(
    prompt: str,
    user: OptionalUser,
):
    user_id = str(user.id) if user else None

    try:
        return generate_response(question=prompt, user_id=user_id)
    except ConnectionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to any database.",
        )
    except AgentError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your query. Please try again.",
        )
