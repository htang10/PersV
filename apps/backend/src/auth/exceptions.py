from fastapi import status


class InvalidCode(Exception):
    pass


class UserNotFound(Exception):
    pass


class InvalidToken(Exception):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid or expired token"
