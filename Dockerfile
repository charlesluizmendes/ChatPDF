FROM python:3.10.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "fastapi[standard]" \
    fastapi-versionizer \
    pymongo \
    pypdf \
    langchain \
    langchain-community \
    langchain-openai \
    langchain-mongodb

COPY . .

EXPOSE 5001

CMD ["python", "run.py"]