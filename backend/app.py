import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.AniZenithExchange import AniZenithRequest, AniZenithResponse
from prometheus.prometheus_middleware import PrometheusMiddleware, prometheus_router
from backend.validation_utils import validate_anizenith_request
from backend.backend_utils import chat_with_llm

from starlette.middleware.sessions import SessionMiddleware
import logging
from dotenv import load_dotenv

load_dotenv("backend/.env")

# Configure logging at Startup
logging.basicConfig(level = logging.INFO)

# Init Logger Instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create FastAPI app
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("BACKEND_SECRET"), session_cookie="session", max_age=3600, same_site="lax")
app.add_middleware(PrometheusMiddleware, prefix="backend")
app.include_router(prometheus_router)
#app.include_router(auth_router)

# ┌───────────────────────────────────────────────┐
# │              BACKEND API ENDPOINTS            │
# └───────────────────────────────────────────────┘
# Chat message handling Endpoint
@app.post("/anizenith/chat", response_model=AniZenithResponse)
async def handle_chat_request(request: AniZenithRequest):
    # Log the request
    logger.info(f"Received Chat Request: {request}")

    # Perform Validations
    validation_error_response = validate_anizenith_request(request)

    # If there was a validation error response, return it
    if validation_error_response:
        return validation_error_response

    # Chat with LLM using the messages in the request
    assistant_message = ""
    for streamed_response in chat_with_llm(request.messages, request.use_local):
        assistant_message = streamed_response

    # Construct an AniZenithResponse based on Assistant Message
    # Copy the old set of messages
    response_messages = request.messages

    # Add the Assistant Message
    response_messages.append({
        "role": "assistant",
        "content": assistant_message
    })

    # Construct an AniZenithResponse and return it
    return AniZenithResponse(messages=response_messages)


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

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
    # uvicorn.run("backend.app:app", host="localhost", port=BACKEND_HTTP_PORT, reload=False, log_level="info")
    uvicorn.run("backend.app:app", 
                host=os.getenv("BACKEND_HOSTNAME"), 
                port=int(os.getenv("BACKEND_PORT")), 
                reload=False, 
                log_level=os.getenv("BACKEND_LOGLEVEL"))