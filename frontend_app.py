import fnmatch
import posixpath

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging

FRONTEND_HTTP_PORT = 7002
#BACKEND_HOST="paffenroth-23.dyn.wpi.edu"
BACKEND_HOST="localhost"
BACKEND_HTTP_PORT=9002

# Configure logging at Startup
logging.basicConfig(level = logging.INFO)

# Init Logger Instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create FastAPI as Frontend App
app = FastAPI()

# Add Middleware security (Only allow requests to specific endpoints to prevent insertion attacks)
origins = [f"http://localhost:{FRONTEND_HTTP_PORT}"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up accessible directories
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Home page endpoint to get our HTML, CSS, JS
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Collect Auth Status from backend
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
        }
    )

# Security middleware endpoint
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    # Add security headers before sending response
    response = await call_next(request)

    CSP = (
        f"default-src 'self'; "
        f"script-src 'self' https://cdn.jsdelivr.net; "
        f"style-src 'self' https://cdnjs.cloudflare.com; "
        f"img-src 'self' data:; "
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

    backend_url = f"http://{BACKEND_HOST}:{BACKEND_HTTP_PORT}/{path}"

    # Store and re-send body to backend
    body_bytes = await request.body()
    body = body_bytes.decode("utf-8")

    try:
        # Logging request forwarded to the backend server
        logger.info(f"Forwarding Request to Backend Server: {backend_url}, body: {body}")

        async with httpx.AsyncClient() as client:
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
    uvicorn.run("frontend_app:app", host="localhost", port=FRONTEND_HTTP_PORT, reload=False, log_level="info")