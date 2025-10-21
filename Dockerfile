FROM python:3.10.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "fastapi[standard]" \
    fastapi-versionizer \
    pymongo \
    pypdf \
    langchain==0.1.20 \
    langchain-core==0.1.52 \
    langchain-community==0.0.38 \
    langchain-openai==0.0.5 \
    gunicorn

COPY . .

ENV PORT=5001
EXPOSE 5001

RUN adduser --disabled-password --gecos '' appuser
USER appuser

CMD ["sh", "-c", "gunicorn src.api.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:${PORT:-5001}"]