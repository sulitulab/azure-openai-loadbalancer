from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("LoggingMiddleware")

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        self.logger.info(f"Request: {request.method} {request.url}")

        try:
            response: Response = await call_next(request)
            duration = time.time() - start_time
            self.logger.info(f"Response: {response.status_code} in {duration:.2f} seconds")
            return response
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error: {str(e)} in {duration:.2f} seconds")
            raise e