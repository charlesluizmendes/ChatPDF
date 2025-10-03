from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi_versionizer.versionizer import Versionizer, api_version

from src.api.error import error_request
from src.api.routes.chatRoutes import router as chatRoutes
from src.api.routes.sourceRoutes import router as sourceRoutes


app = FastAPI(
    title="ChatPDF",
    description="API de RAG utilizando LLM do OpenAI e MongoDB Atlas.",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.middleware("http")(error_request)

app.include_router(chatRoutes)
app.include_router(sourceRoutes)

versions = Versionizer(
    app=app,
    prefix_format='/api/v{major}',
    semantic_version_format='{major}',
    latest_prefix='/api/latest',
    sort_routes=True
).versionize()

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/api/latest/docs")