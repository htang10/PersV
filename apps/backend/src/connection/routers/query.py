from fastapi import APIRouter, HTTPException, status

from src.agent.executor import generate_response
from src.agent.schemas import QueryResponse
from src.connection.database import custom_conn_manager
from src.connection.demo_samples import pick_demo_samples
from src.connection.dependencies.anon_id import UserId
from src.connection.exceptions import AgentError
from src.connection.schemas import QueryRequest

router = APIRouter()


@router.post(
    "/query",
    summary="Query the database",
    description="Ask a question in plain English and get an answer drawn directly from your data.",
    response_model=QueryResponse,
)
async def query(user_id: UserId, request: QueryRequest):
    # If successful, reset the connection expiry for user every time they query
    if not user_id or not custom_conn_manager.reset_expiry(user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active database connection found.",
        )

    try:
        response = await generate_response(prompt=request.prompt, user_id=user_id)
        if not response.sql:
            # Suggests users what they can ask if their current question couldn't be answered
            response.suggestions = pick_demo_samples()
        return response
    except AgentError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent service is unavailable at the moment. Please try again later.",
        )
