import uvicorn
from app.core.settings import app
from app.frontend.routes import router


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
