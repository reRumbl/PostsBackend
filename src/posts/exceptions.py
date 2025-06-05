from fastapi import HTTPException, status


class InvalidFileTypeException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid file type'
        )
        
    
class UserNotPostAuthorException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User is not author of this post'
        )
