import os
from dotenv import load_dotenv

from src.infrastructure.context.mongoContext import MongoContext
from src.infrastructure.repositories.pdfRepository import PdfRepository
from src.infrastructure.repositories.vectorRepository import VectorRepository
from src.infrastructure.services.llmService import LlmService

load_dotenv(".env", override=True)


MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION_VECTORS = os.getenv("MONGO_COLLECTION_VECTORS")
MONGO_COLLECTION_DOCS = os.getenv("MONGO_COLLECTION_DOCS")
MONGO_INDEX_NAME = os.getenv("MONGO_INDEX_NAME")

OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_KEY = os.getenv("OPENAI_KEY")
OPENAI_TEMPERATURE = os.getenv("OPENAI_TEMPERATURE")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))

_mongodb_context = None

def get_mongodb_context() -> MongoContext:
    global _mongodb_context
    if _mongodb_context is None:
        _mongodb_context = MongoContext(MONGO_URL, MONGO_DB, OPENAI_KEY)
    return _mongodb_context

def get_pdf_repository() -> PdfRepository:
    context = get_mongodb_context()
    return PdfRepository(context, MONGO_COLLECTION_DOCS)

def get_vector_repository() -> VectorRepository:
    context = get_mongodb_context()
    return VectorRepository(
        context=context,
        collection_name=MONGO_COLLECTION_VECTORS,
        index_name=MONGO_INDEX_NAME,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

def get_llm_service() -> LlmService:
    return LlmService(
        model=OPENAI_MODEL,
        api_key=OPENAI_KEY,
        temperature=OPENAI_TEMPERATURE
    )