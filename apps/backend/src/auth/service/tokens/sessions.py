"""User sessions: a capped record of each user's active refresh tokens.

A session is identified by its hashed refresh token, so revoking a session and
revoking its token are the same action. Each user keeps at most
`MAX_USER_SESSIONS` sessions. When the limit is exceeded, the oldest are
evicted and their tokens revoked, which bounds per-user storage and allows
every session to be ended at once.
"""

from src.auth.config import auth_settings
from src.auth.service.tokens.keys import RefreshTokenKey, SessionKey
from src.core.redis_client import redis_client
from src.core.utils import get_current_datetime


def register_user_session(user_id: str, session_id: str) -> None:
    """Registers a new session for a user, evicting the oldest if over the limit.

    Evicted sessions have their refresh tokens revoked, so their holders must
    sign in again.

    Args:
        user_id: ID of the user the session belongs to.
        session_id: The hashed refresh token that identifies the session.
    """
    session_key = SessionKey.for_user(user_id)

    # Register the new session
    redis_client.zadd(
        name=session_key,
        mapping={
            session_id: get_current_datetime().timestamp()
        },  # Redis sorted set's scores are numeric
    )

    # Keep only the 3 newest sessions, clean up the rest
    old_sessions = redis_client.zrange(
        name=session_key,
        start=0,
        end=-(auth_settings.MAX_USER_SESSIONS + 1),
    )

    if old_sessions:
        redis_client.delete(
            *(RefreshTokenKey.for_token(token) for token in old_sessions)
        )
        redis_client.zrem(
            session_key,
            *old_sessions,
        )


def revoke_user_session(user_id: str, session_id: str) -> None:
    """Removes a single session from a user's active sessions.

    Does not revoke the refresh token itself. Callers revoke the token
    separately. Does nothing if the session is not registered.

    Args:
        user_id: ID of the user the session belongs to.
        session_id: The hashed refresh token that identifies the session.
    """
    session_key = SessionKey.for_user(user_id)
    redis_client.zrem(
        session_key,
        session_id,
    )


def revoke_all_user_sessions(user_id: str) -> None:
    """Revokes every refresh token and session belonging to a user.

    Args:
        user_id: ID of the user whose sessions should all be revoked.
    """
    session_key = SessionKey.for_user(user_id)
    # Retrieve all refresh tokens user has using their id
    session_ids = redis_client.zrange(session_key, 0, -1)
    if not session_ids:
        return

    # Batch all the deletes into one single round-trip instead of N separate calls
    pipe = redis_client.pipeline()
    for session_id in session_ids:
        # First, delete all refresh tokens user has
        pipe.delete(RefreshTokenKey.for_token(session_id))
    # Finally delete all of their associated sessions
    pipe.delete(session_key)
    pipe.execute()
