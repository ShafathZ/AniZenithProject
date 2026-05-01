import fnmatch
import posixpath
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging

from common.prometheus.prometheus_middleware import PrometheusMiddleware, prometheus_router

from frontend.configs import frontend_container_config, frontend_app_config

# Configure logging at Startup
logging.basicConfig(level = logging.INFO)

# Init Logger Instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create FastAPI as Frontend App
app = FastAPI()

# Add Middleware security (Only allow requests to specific endpoints to prevent insertion attacks)
origins = [f"http://{frontend_container_config.hostname}:{frontend_container_config.port}"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PrometheusMiddleware, prefix="frontend")
app.include_router(prometheus_router)

# Set up accessible directories
SERVICE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=SERVICE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=SERVICE_DIR / "templates")

# Home page endpoint to get our HTML, CSS, JS
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Collect Auth Status from backend
    return templates.TemplateResponse(
        "chatbot.html",
        {
            "request": request,
        }
    )

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request):
    # Return template for search page
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    # Return template for About Us page
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/favorites", response_class=HTMLResponse)
async def favorites(request: Request):
    # Return template for About Us page
    return templates.TemplateResponse("favorites.html", {"request": request})

# Security middleware endpoint
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Add security headers before sending response
    response = await call_next(request)

    CSP = (
        f"default-src 'self'; "
        f"script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        f"style-src 'self' https://cdnjs.cloudflare.com; "
        f"img-src 'self' https://cdn.myanimelist.net data:; "
        f"font-src 'self' https://cdnjs.cloudflare.com; "
        f"frame-ancestors 'none';"
    )
    response.headers["Content-Security-Policy"] = CSP
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# --------- PROXY ENDPOINT ----------
ALLOWED_PROXY_ROUTES = {
    "anizenith/chat": ["POST"],
    "anizenith/search": ["GET"],
    "login/*": ["GET", "HEAD"],
    "logout/*": ["POST"],
    "auth/status": ["GET"],
    "mal/*": ["GET", "POST"]
}

def is_allowed_route(path: str, method: str) -> bool:
    method = method.upper()
    # Glob-based search for if route is allowed (Using loop because not many endpoints in our proxy allowed)
    for pattern, methods in ALLOWED_PROXY_ROUTES.items():
        if fnmatch.fnmatch(path, pattern) and method in methods:
            return True
    return False

# Proxy endpoint for posting requests to backend
# Usage: Send POST to "localhost:7002/proxy/anizenith/chat"
@app.api_route("/proxy/{path:path}", methods=["GET", "POST", "HEAD"])
async def proxy(path: str, request: Request):
    # Simple way to prevent /.. or other local path tricks
    path = posixpath.normpath(path).lstrip("/")
    if not is_allowed_route(path, request.method):
        return JSONResponse({"error": "Endpoint not allowed through proxy"}, status_code=403)

    backend_url = f"http://{frontend_app_config.proxy_hostname}:{frontend_app_config.proxy_port}/{path}"

    # Store and re-send body to backend
    body_bytes = await request.body()
    body = body_bytes.decode("utf-8")

    # Get timeout duration if it exists (or use default)
    timeout = 5.0
    try:
        timeout = float(request.headers.get("X-Request-Timeout", timeout))
    except ValueError:
        pass

    try:
        # Logging request forwarded to the backend server
        logger.info(f"Forwarding Request to Backend Server: {backend_url}, body: {body}, timeout: {timeout}")

        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
            backend_response = await client.request(
                method=request.method.upper(),
                url=backend_url,
                content=body,
                headers=dict(request.headers),
                params=request.query_params,
            )
    except (httpx.ConnectError, httpx.TimeoutException):
        return JSONResponse({"error": "Backend server has timed out. Please try again later."}, status_code=504)
    except httpx.RequestError:
        return JSONResponse({"error": "Internal Server Error."}, status_code=500)

    return Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=dict(backend_response.headers)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,
                host=frontend_container_config.hostname,
                port=frontend_container_config.port,
                reload=False,
                log_level=frontend_app_config.log_level)