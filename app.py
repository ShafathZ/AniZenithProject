from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from backend.AniZenithExchange import AniZenithRequest, AniZenithResponse
from backend.validation_utils import validate_anizenith_request
import logging

# Configure logging at Startup
logging.basicConfig(
    level = logging.INFO,
)

# Init Logger Instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create FastAPI app
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

# ┌───────────────────────────────────────────────┐
# │              BACKEND API ENDPOINTS            │
# └───────────────────────────────────────────────┘

# Chat message handling Endpoint
@app.post("/anizenith/chat", response_model=AniZenithResponse)
async def handle_chat_request(request: AniZenithRequest):
    # Log the request
    logger.info(f"Received Chat Request: {request}")

    # TODO: Perform Validations
    validation_error_response = validate_anizenith_request(request)
    if validation_error_response:
        return validation_error_response

    # TODO: Call Backend Utils

    # TODO: Construct an AniZenithResponse based on output from Backend Utils
    response_messages = request.messages
    response = AniZenithResponse(messages=response_messages)

    # Return the AniZenithResponse
    return response


# ┌───────────────────────────────────────────────┐
# │                EXCEPTION HANDLERS             │
# └───────────────────────────────────────────────┘

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, err: RequestValidationError):
    logger.error(f"Validation error on {request.url.path}, error: {err.errors()}")

    error_response_content = {
        "message": "Request Body Validation Failed",
        "details": []
    }

    # Iterate over all individual errors
    for error in err.errors():

        # If type of error is "json_invalid"
        if error['type'] == "json_invalid":
            error_response_content["details"].append(
                {"field": "response_body", "reason": "Invalid JSON"}
            )

        # If type of error is "missing"
        if error['type'] == "missing":
            error_response_content["details"].append(
                {"field": error['loc'][1], "reason": "Required Field Missing"}
            )

        # TODO: Add More Cases to make error handling more robust

    return JSONResponse(
        status_code=400,
        content = error_response_content
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="localhost", port=4007, reload=True, log_level="info")