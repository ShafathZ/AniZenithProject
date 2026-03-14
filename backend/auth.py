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
OAUTH_PROVIDERS = ["mal"]
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
# TODO: Change localhost to public facing backend callback endpoint (We have to do it this way because we don't have a third authentication server)
BACKEND_HTTP_PORT = 9002
REDIRECT_URI = f"http://localhost:{BACKEND_HTTP_PORT}/callback/mal"

@router.get("/login/mal")
async def mal_login(request: Request):
    # I hate OAuth2
    code_verifier = secrets.token_urlsafe(64)
    request.session['verifier'] = code_verifier

    # Use Referral method to get frontend IP (Scalable with multiple frontend servers)
    origin_url = request.headers.get("Origin") or request.headers.get("Referer")
    request.session['origin_url'] = origin_url

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
    # Send user back to original frontend page
    origin_url = request.session.pop("origin_url")

    # Add OAuth token
    auth_tokens = request.session.setdefault("auth_tokens", {})
    auth_tokens["mal"] = token["access_token"]
    return RedirectResponse(origin_url)

@router.post("/logout")
async def logout(request: Request):
    # TODO: Make this more robust than just clearing entire session in case we use session cookie for something else
    request.session.clear()
    return JSONResponse({"auth_tokens": request.session.get("auth_tokens")})

@router.get("/auth/status")
async def auth_status(request: Request):
    # Get the auth tokens currently accessible
    return JSONResponse({"auth_tokens": request.session.get("auth_tokens")})

# Error handling decorator for API in case key does not exist/bad auth
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

# Testing endpoint to get my own profile
@router.get("/mal/profile")
@oauth_error_handler
async def mal_profile(request: Request):
    # Fetch tokens from DB
    access_token = request.session["auth_tokens"]["mal"]

    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.myanimelist.net/v2/users/@me", headers=headers)
        response.raise_for_status()

    return response.json()