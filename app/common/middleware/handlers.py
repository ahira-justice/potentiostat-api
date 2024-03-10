import time

from fastapi import Request, Response
from loguru import logger


async def http_logging_middleware(request: Request, call_next):
    start_time = time.time()

    logger.info(f"Running request '{request.method} > {request.url}'")

    response: Response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"Finished running request '{request.method} > {request.url}' in {process_time} seconds")
    logger.info(f"Response Status Code: {response.status_code}")

    return response
