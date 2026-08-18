# ruff: noqa: ANN201
from fastapi import APIRouter, HTTPException, status

from src.auth.dependencies import OptionalUser
from src.pipeline.agent.executor import generate_response
from src.pipeline.database import custom_conn_manager
from src.pipeline.exceptions import AgentError
from src.pipeline.schemas import QueryResponse

router = APIRouter()


@router.post(
    "/query",
    summary="Query the database",
    description="Ask a question in plain English and get an answer drawn directly from your data.",
    response_model=QueryResponse,
)
async def query(
    prompt: str,
    user: OptionalUser,
):
    user_id = str(user.id) if user else None
    if user_id:
        success = custom_conn_manager.reset_expiry(user_id=user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not connected to any database.",
            )

    try:
        return await generate_response(question=prompt, user_id=user_id)
    except AgentError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your query. Please try again.",
        )
