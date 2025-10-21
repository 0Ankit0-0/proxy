from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import APP_NAME, APP_VERSION, DEBUG, ALLOWED_HOSTS
from routes import logs, analysis, soup, health

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    debug=DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(logs.router, prefix="/logs", tags=["Logs"])
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
app.include_router(soup.router, prefix="/soup", tags=["Soup"])

app.get("/")
def root():
    return {"message": f"Welcome to {APP_NAME} API!"}