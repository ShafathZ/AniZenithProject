from fastapi import APIRouter, Response, Request
import prometheus_client
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Summary
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

# ----- Prometheus Client Server -----
# TODO: Configure this externally
prometheus_client.start_http_server(9000)

# ----- Prometheus HTTP Request Middleware -----
class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that records Prometheus metrics for all HTTP requests.

    It measures request count, response count, and latency by intercepting requests.
    Labels of metrics include the method, endpoint, and status code when necessary.
    """

    # Prefix here if the middleware is used to identify a specific FastAPI app on a shared Prometheus server
    def __init__(self, app, prefix="app"):
        super().__init__(app)

        # Init Prometheus metrics stores/counters for HTTP requests
        self.HTTP_REQUESTS_TOTAL = Counter(
            f"{prefix}_requests_total",
            "Total HTTP requests received by the application (w/ response status)",
            ["method", "endpoint"]
        )

        self.HTTP_REQUEST_LATENCY = Summary(
            f"{prefix}_request_latency_seconds",
            "Time spent processing an HTTP request in seconds",
            ["method", "endpoint"]
        )

        self.HTTP_RESPONSES_TOTAL = Counter(
            f"{prefix}_responses_total",
            "Total number of responses sent by the application",
            ["method", "endpoint", "status"]
        )


    async def dispatch(self, request: Request, call_next):
        """
        Middleware for tracking HTTP requests and latency with Prometheus.
        dispatch is method called through the middleware pipeline in FastAPI to push through requests.
        FastAPI handles Middleware by passing every request through here before passing into app,
        and then returning back here via "await call_next(request)" to handle responses.
        """

        # Add the request to counter
        endpoint = request.scope.get("path", request.url.path)
        self.HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=endpoint
        ).inc()

        with self.HTTP_REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).time():
            # Run the HTTP call through middleware
            try:
                response = await call_next(request)
            except Exception as exc:
                # Count exceptions as 500
                self.HTTP_RESPONSES_TOTAL.labels(
                    method=request.method,
                    endpoint=endpoint,
                    status="500"
                ).inc()
                raise exc

            # Get how long the request took to process
            self.HTTP_RESPONSES_TOTAL.labels(method=request.method,
                                             endpoint=endpoint,
                                             status=str(response.status_code)).inc()

        return response