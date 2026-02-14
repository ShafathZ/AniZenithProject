from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

# Chat message handling
@app.post("/chat")
async def send_chat(request: Request):
    data = await request.json()

    return JSONResponse({
        "response": data
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="localhost", port=4007, reload=True)