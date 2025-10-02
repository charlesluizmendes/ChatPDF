from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.api.error import error_request
from src.api.routes.chatRoutes import router as chatRoutes
from src.api.routes.sourceRoutes import router as sourceRoutes


app = FastAPI(
    title="ChatPDF",
    description="API do ChatPDF",
    version="1.0.0"
)

app.middleware("http")(error_request)

app.include_router(chatRoutes)
app.include_router(sourceRoutes)

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")