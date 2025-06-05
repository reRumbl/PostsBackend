import logging
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from src.schemas import SuccessResponse
from src.auth.router import router as auth_router
from src.posts.router import router as posts_router
from src.redis_client.dependencies import get_redis_client
from src.config import settings
from src.logging_config import setup_logging

# --- App lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before startup
    setup_logging()
    redis_client = get_redis_client()
    if not await redis_client.is_connected():
        logging.getLogger('error_logger').error('Error with redis connection')
    else:
        FastAPICache.init(RedisBackend(redis_client.connection), prefix='fastapi_cache')
    
    yield

    # After shutdown
    ...


# --- App initialization ---

app = FastAPI(lifespan=lifespan, title='Posts', docs_url='/api/docs', redoc_url=None)

# --- Routers ---

app.include_router(auth_router)
app.include_router(posts_router)

# --- Middlewares ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allow_headers=['*'],
    expose_headers=['*'],
    allow_credentials=True
)

# --- Base routes ---


@app.get('/api')
async def root():
    return SuccessResponse(message='Server is active!')


# --- Start script ---

if __name__ == '__main__':
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
