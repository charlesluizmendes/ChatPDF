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
    langchain-openai==0.0.5

COPY . .

EXPOSE 5001

CMD ["python", "run.py"]