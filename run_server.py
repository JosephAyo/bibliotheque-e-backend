import os
import uvicorn
from dotenv import load_dotenv

load_dotenv(".env")

PORT = int(os.getenv("PORT", 10000))
ENV = os.getenv("ENV", "development")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", port=PORT, log_level="info", reload=ENV == "development"
    )
