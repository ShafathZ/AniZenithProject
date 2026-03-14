import os
import secrets
from functools import wraps
import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth

# Central configuration for all OAuth authentication
PROVIDER_CONFIG = {
    "mal": {
        "client_id": os.getenv("MAL_CLIENT_ID"),
        "client_secret": os.getenv("MAL_CLIENT_SECRET"),
        "access_token_url": "https://myanimelist.net/v1/oauth2/token",
        "authorize_url": "https://myanimelist.net/v1/oauth2/authorize",
        "client_kwargs": {"code_challenge_method": "plain"},
    }
}

# Single OAuth and API router
oauth = OAuth()
router = APIRouter()

# Base Redirect URL of Auth server (Our Auth server = Backend server currently)
# TODO: Move these at some point to centralized config
BACKEND_HTTP_PORT = 9002
BASE_REDIRECT_URI = f"http://localhost:{BACKEND_HTTP_PORT}"

# Error handling
def oauth_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except KeyError:
            return JSONResponse({"error": "No access token found. Please log in."}, status_code=401)
        except httpx.TimeoutException:
            return JSONResponse({"error": "Authentication servers are down. Please try again later."}, status_code=504)
        except httpx.HTTPStatusError as e:
            return JSONResponse({"error": f"Error Authenticating: {e.response.status_code}"}, status_code=e.response.status_code)
        except Exception as e:
            return JSONResponse({"error": "Error Authenticating", "details": str(e)}, status_code=500)
    return wrapper


# Adding App routes for each OAuth endpoint
def add_provider_routes(provider: str):
    # Login endpoint
    async def login(request: Request):
        code_verifier = secrets.token_urlsafe(64)
        # Store provider-specific values in session
        request.session[f"{provider}_verifier"] = code_verifier

        origin_url = request.headers.get("Origin") or request.headers.get("Referer")
        request.session[f"{provider}_origin_url"] = origin_url

        redirect_uri = f"{BASE_REDIRECT_URI}/callback/{provider}"
        client = oauth.create_client(provider)
        return await client.authorize_redirect(
            request,
            redirect_uri,
            code_challenge=code_verifier,
            code_challenge_method="plain",
        )

    # HEAD request for auth server (returns 200 OK)
    async def login_head():
        return Response(status_code=200)

    # Callback endpoint after OAuth2 success
    async def callback(request: Request):
        code_verifier = request.session.pop(f"{provider}_verifier", None)
        code = request.query_params.get("code")
        origin_url = request.session.pop(f"{provider}_origin_url", None)

        if not code or not code_verifier:
            return RedirectResponse(origin_url or "/")

        redirect_uri = f"{BASE_REDIRECT_URI}/callback/{provider}"
        client = oauth.create_client(provider)
        token = await client.fetch_access_token(
            code_verifier=code_verifier,
            redirect_uri=redirect_uri,
            code=code,
        )

        auth_tokens = request.session.setdefault("auth_tokens", {})
        auth_tokens[provider] = token["access_token"]
        return RedirectResponse(origin_url or "/")

    # Add routes
    router.add_api_route(f"/login/{provider}", login, methods=["GET"])
    router.add_api_route(f"/login/{provider}", login_head, methods=["HEAD"])
    router.add_api_route(f"/callback/{provider}", callback, methods=["GET"])

# ----- REGISTER ALL OAUTH ENDPOINTS -----
for provider, config in PROVIDER_CONFIG.items():
    # Register OAuth2 server
    oauth.register(
        name=provider,
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        access_token_url=config["access_token_url"],
        authorize_url=config["authorize_url"],
        client_kwargs=config.get("client_kwargs", {}),
    )

    # Add provider's app routes
    add_provider_routes(provider)


# Logout node
@router.post("/logout/{provider}")
async def logout(request: Request, provider: str):
    # Remove specific OAuth provider tokens
    auth_tokens = request.session.get("auth_tokens", {})
    if provider in auth_tokens:
        del auth_tokens[provider]
        request.session["auth_tokens"] = auth_tokens
    return JSONResponse({"auth_tokens": request.session.get("auth_tokens")})

# Auth status
@router.get("/auth/status")
async def auth_status(request: Request):
    return JSONResponse({"auth_tokens": request.session.get("auth_tokens")})

# ----- SPECIFIC ENDPOINTS -----
# Testing endpoint to get my own profile
@router.get("/mal/profile")
@oauth_error_handler
async def mal_profile(request: Request):
    access_token = request.session["auth_tokens"]["mal"]

    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.myanimelist.net/v2/users/@me", headers=headers)
        response.raise_for_status()

    return response.json()