from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

from config import APP_NAME, APP_VERSION, DEBUG, ALLOWED_HOSTS, API_HOST, DEPLOYMENT_MODE, LOGS_DIR
from core.isolation_validator import IsolationValidator
from routes import logs, analysis, soup, health

# Configure logging to both file and console
log_file = LOGS_DIR / 'server.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

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

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log incoming request
    logger.info(f"REQUEST: {request.method} {request.url} - Client: {request.client.host if request.client else 'unknown'}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response
        logger.info(f"RESPONSE: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.3f}s")

        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"ERROR: {request.method} {request.url} - Exception: {str(e)} - Time: {process_time:.3f}s")
        raise

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
