class RefreshTokenKey:
    """Key for a stored refresh token.

    key:
        refresh_token:{hashed_refresh_token}
    value: user_id
    """

    PREFIX = "refresh_token"

    @classmethod
    def for_token(cls, hashed_token: str) -> str:
        """Builds the key for a hashed refresh token.

        Args:
            hashed_token: The hashed refresh token.

        Returns:
            The key.
        """
        return f"{cls.PREFIX}:{hashed_token}"


class SessionKey:
    """Key for a user's active sessions.

    key:
        user_session:{user_id}
    values:
        - session_id1, created_at
        - session_id2, created_at
        ...
        - session_id5, created_at

    Each session id is a hashed refresh token.
    """

    PREFIX = "user_session"

    @classmethod
    def for_user(cls, user_id: str) -> str:
        """Builds the key for a user's sessions.

        Args:
            user_id: ID of the user.

        Returns:
            The key.
        """
        return f"{cls.PREFIX}:{user_id}"


class RotatedTokenKey:
    """Key for the marker left behind when a refresh token is rotated.

    key:
        rotated:{hashed_refresh_token}
    value: user_id
    """

    PREFIX = "rotated"

    @classmethod
    def for_token(cls, hashed_token: str) -> str:
        """Builds the key for a rotated, hashed refresh token.

        Args:
            hashed_token: The hashed refresh token that was rotated.

        Returns:
            The key.
        """
        return f"{cls.PREFIX}:{hashed_token}"
