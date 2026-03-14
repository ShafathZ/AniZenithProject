import json

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

# Set up accessible directories
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Collect Auth Status from backend
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
        }
    )

# Proxy endpoint for posting requests to backend
# Usage: Send POST to "localhost:7002/proxy/anizenith/chat"
@app.api_route("/proxy/{path:path}", methods=["GET", "POST", "HEAD"])
async def proxy(path: str, request: Request):
    backend_url = f"http://{BACKEND_HOST}:{BACKEND_HTTP_PORT}/{path}"

    # Store and re-send body to backend
    body_bytes = await request.body()
    body = body_bytes.decode("utf-8")

    # Forward request to backend via async http request
    try:
        async with httpx.AsyncClient() as client:
            backend_response = await client.request(
                method=request.method.upper(),
                url=backend_url,
                content=body,
                headers=dict(request.headers),
                params=request.query_params,
            )
    except (httpx.ConnectError, httpx.TimeoutException):
        # Cant connect to backend via proxy
        return JSONResponse({"error": "Backend server has timed out. Please try again later."}, status_code=504)

    except httpx.RequestError as e:
        # Other httpx errors
        return JSONResponse({"error": f"Backend request failed."}, status_code=502)

    # Return backend response directly
    return Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=dict(backend_response.headers)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("frontend_app:app", host="localhost", port=FRONTEND_HTTP_PORT, reload=False, log_level="info")