import time

from fastapi import APIRouter, Response, Request
import prometheus_client
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

# ----- Prometheus Client Endpoints -----
prometheus_router = APIRouter()

# Endpoint for getting all prometheus client content
@prometheus_router.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Additional Prometheus Client Server
# TODO: Configure this externally
prometheus_client.start_http_server(9001)

# Prometheus HTTP Request Middleware
class PrometheusMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, prefix="http"):
        super().__init__(app)

        # Add Prometheus Client HTTP Client Common Data


        self.HTTP_REQUESTS_TOTAL = Counter(
            f"{prefix}_requests_total",
            "Total HTTP requests received by the application (w/ response status)",
            ["method", "endpoint", "status"]
        )

        self.HTTP_REQUEST_LATENCY = Histogram(
            f"{prefix}_request_latency_seconds",
            "HTTP request latency in seconds",
            ["method", "endpoint"]
        )

        self.HTTP_RESPONSES_TOTAL = Counter(
            f"{prefix}_responses_total",
            "Total number of responses sent by the application",
            ["endpoint", "status"]
        )


    """
    Middleware for tracking HTTP requests and latency with Prometheus.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        # Run the HTTP call through middleware
        try:
            response = await call_next(request)
        except Exception as exc:
            # Count exceptions as 500
            endpoint = request.scope.get("route").path if request.scope.get("route") else request.url.path
            self.HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=endpoint,
                status="500"
            ).inc()
            raise exc

        # Get how long the request took to process
        latency = time.time() - start_time
        endpoint = request.scope.get("route").path if request.scope.get("route") else request.url.path

        self.HTTP_REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(latency)
        self.HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=endpoint,
            status=str(response.status_code)
        ).inc()
        self.HTTP_RESPONSES_TOTAL.labels(endpoint=endpoint, status=str(response.status_code)).inc()

        return response