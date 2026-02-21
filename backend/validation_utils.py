from backend.AniZenithExchange import AniZenithRequest
from fastapi.responses import JSONResponse


def validate_anizenith_request(request: AniZenithRequest) -> None | JSONResponse:
    error_response_content = {
        "message": "Request Body Validation Failed",
        "details": []
    }
    
    num_errors_detected = 0

    # Check for Empty Messages
    if len(request.messages) == 0:
        num_errors_detected += 1
        error_response_content["details"].append(
            {"field": "messages", "reason": "messages are empty, please provide atleast a \'user\' message."}
        )

    # Check for Last Message being a 'user' message
    if len(request.messages) > 0 and request.messages[-1]['role'] != 'user':
        num_errors_detected += 1
        error_response_content["details"].append(
            {"field": "messages", "reason": "Last message in the list should be a \'user\' message."}
        )

    # Check for Presence of System Prompt
    for message in request.messages:
        if message["role"] == "system":
            num_errors_detected += 1
            error_response_content["details"].append(
                {"field": "messages", "reason": "Sending messages with role as \'system\' is not permitted!"}
            )
            break

    # If no errors are detected, return empty object
    if num_errors_detected == 0:
        return
    
    # Else return a JSONResponse with Error Details
    else:
        return JSONResponse(
            status_code=400,
            content = error_response_content
        )