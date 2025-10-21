import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=port, reload=True)