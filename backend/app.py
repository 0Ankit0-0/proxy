from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import APP_NAME, APP_VERSION, DEBUG, ALLOWED_HOSTS, API_HOST, DEPLOYMENT_MODE
from core.isolation_validator import IsolationValidator
from routes import logs, analysis, soup, health

logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    debug=DEBUG
)

# CORS Middleware with deployment-aware configuration
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


@app.on_event("startup")
async def startup_validation():
    """
    Validate deployment configuration on startup
    Warns if running in insecure mode
    """
    logger.info("=" * 70)
    logger.info(f"🚀 {APP_NAME} v{APP_VERSION} Starting...")
    logger.info(f"📍 Deployment Mode: {DEPLOYMENT_MODE.upper()}")
    logger.info(f"🌐 API Host: {API_HOST}")
    logger.info("=" * 70)
    
    # Run isolation validation
    validator = IsolationValidator()
    report = validator.validate_isolation()
    
    logger.info(f"🔒 Isolation Level: {report['isolation_level']}")
    
    if report['warnings']:
        logger.warning("⚠️ Isolation Warnings:")
        for warning in report['warnings']:
            logger.warning(f"   {warning}")
    
    if DEPLOYMENT_MODE == "debug":
        logger.warning("=" * 70)
        logger.warning("⚠️⚠️⚠️ RUNNING IN DEBUG MODE - INSECURE ⚠️⚠️⚠️")
        logger.warning("DO NOT USE IN PRODUCTION OR SENSITIVE ENVIRONMENTS")
        logger.warning("=" * 70)
    
    elif DEPLOYMENT_MODE == "isolated" and not report['compliant']:
        logger.warning("=" * 70)
        logger.warning("⚠️ ISOLATED mode configured but system is not fully isolated")
        logger.warning("Review warnings above")
        logger.warning("=" * 70)
    
    logger.info("✅ Startup validation complete")


@app.get("/")
def root():
    """Root endpoint with deployment info"""
    return {
        "message": f"Welcome to {APP_NAME} API!",
        "version": APP_VERSION,
        "deployment_mode": DEPLOYMENT_MODE,
        "api_host": API_HOST,
        "endpoints": {
            "health": "/health/",
            "isolation_check": "/health/isolation",
            "docs": "/docs",
        }
    }
