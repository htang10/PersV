# ruff: noqa: ANN201
from fastapi import APIRouter, HTTPException, Response, status

from src.agent.executor import generate_response
from src.agent.schemas import QueryResponse
from src.auth.dependencies import OptionalUserId
from src.auth.service.identities import is_valid_anon_id, set_anon_id_cookie
from src.pipeline.database import custom_conn_manager
from src.pipeline.exceptions import AgentError

router = APIRouter()


@router.post(
    "/query",
    summary="Query the database",
    description="Ask a question in plain English and get an answer drawn directly from your data.",
    response_model=QueryResponse,
)
async def query(response: Response, prompt: str, user_id: OptionalUserId):
    if not user_id or not custom_conn_manager.reset_expiry(user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to any database.",
        )

    try:
        if is_valid_anon_id(user_id):
            set_anon_id_cookie(response, anon_id=user_id)
        return await generate_response(question=prompt, user_id=user_id)
    except AgentError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your query. Please try again.",
        )
