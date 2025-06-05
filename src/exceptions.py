from fastapi import HTTPException, status


class InternalServerError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server error',
        )


class BadRequest(HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or 'Bad request',
        )
