import logging
from functools import wraps
from fastapi import HTTPException
from src.exceptions import InternalServerError


def default_router_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as ex:
            raise ex
        except Exception as ex:
            logging.getLogger('error_logger').error(str(ex))
            raise InternalServerError()
    return wrapper
