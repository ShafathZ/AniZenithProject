import os
from functools import wraps

import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
import secrets

# Make API Router to connect to main App
router = APIRouter()

# OAuth Client Library
oauth = OAuth()
mal = oauth.register(
    name="mal",
    client_id=os.getenv("MAL_CLIENT_ID"),
    client_secret=os.getenv("MAL_CLIENT_SECRET"),
    access_token_url="https://myanimelist.net/v1/oauth2/token",
    authorize_url="https://myanimelist.net/v1/oauth2/authorize",
    client_kwargs={'code_challenge_method': 'plain'}
)

# ┌───────────────────────────────────────────────┐
# │          MyAnimeList OAuth Endpoint           │
# └───────────────────────────────────────────────┘
# TODO: Move these to better place
BACKEND_HTTP_PORT = 9002
REDIRECT_URI = f"http://localhost:{BACKEND_HTTP_PORT}/callback/mal"
FRONTEND_URL = "http://localhost:7002/"

@router.get("/login/mal")
async def login(request: Request):
    # I hate OAuth2
    code_verifier = secrets.token_urlsafe(64)
    request.session['verifier'] = code_verifier
    return await mal.authorize_redirect(request, REDIRECT_URI, code_challenge=code_verifier, code_challenge_method="plain")

@router.get("/callback/mal")
async def mal_callback(request: Request):
    # Exchange code for access token via callback
    code_verifier = request.session.pop("verifier")
    if not code_verifier:
        return {"error": "Missing PKCE verifier"}

    token = await mal.fetch_access_token(
        code_verifier=code_verifier,
        redirect_uri=REDIRECT_URI,
        code=request.query_params.get("code")
    )
    request.session["mal_access_token"] = token["access_token"]
    return RedirectResponse(f"{FRONTEND_URL}?login=success")

@router.get("/logout")
async def logout(request: Request):
    # TODO: Make this more robust than just clearing entire session in case we use session cookie for something else
    request.session.clear()
    return RedirectResponse(FRONTEND_URL)

@router.get("/auth/status")
async def auth_status(request: Request):
    # Dynamically checks all OAuth logins and sends back in this get request (In case we do more OAuth)
    providers = ["mal"]
    logged_in_nodes = {}

    for provider in providers:
        session_key = f"{provider}_access_token"
        if session_key in request.session:
            logged_in_nodes[provider] = True

    return JSONResponse({"nodes": logged_in_nodes})

# Error handling decorator for API in case key does not exist/bad auth
def mal_error_handler(func):
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

# Testing endpoint to get my own profile
@router.get("/mal/profile")
@mal_error_handler
async def mal_profile(request: Request):
    # Fetch tokens from DB
    access_token = request.session.get("mal_access_token")

    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.myanimelist.net/v2/users/@me", headers=headers)
        response.raise_for_status()

    return response.json()