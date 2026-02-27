import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

from starlette.responses import JSONResponse

FRONTEND_HTTP_PORT = 7002
BACKEND_HOST="paffenroth-23.dyn.wpi.edu"
BACKEND_HTTP_PORT=9002

# Configure logging at Startup
logging.basicConfig(
    level = logging.INFO,
)

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
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )

# Proxy endpoint for posting requests to backend
# Usage: Send POST to "localhost:7002/proxy/anizenith/chat"
@app.post("/proxy/{path:path}")
async def proxy(path: str, request: Request):
    backend_url = f"http://{BACKEND_HOST}:{BACKEND_HTTP_PORT}/{path}"

    # Store and re-send body to backend
    body = await request.body()

    # Forward request to backend via async http request
    async with httpx.AsyncClient() as client:
        backend_response = await client.post(
            backend_url,
            content=body,
            headers=dict(request.headers),
            params=request.query_params,
        )

    # Return backend response directly
    return JSONResponse(
        content=backend_response.json(),
        status_code=backend_response.status_code
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("frontend_app:app", host="localhost", port=FRONTEND_HTTP_PORT, reload=False, log_level="info")