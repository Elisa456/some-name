from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
import logging
import os

from app.database import engine, Base
from app.api.v1 import applications, auth, portfolio, reviews, statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Landscape Design API",
    description="API для строительства.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

app.include_router(applications.router, prefix="/api/v1", tags=["applications"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(portfolio.router, prefix="/api/v1", tags=["portfolio"])
app.include_router(reviews.router, prefix="/api/v1", tags=["reviews"])
app.include_router(statistics.router, prefix="/api/v1", tags=["statistics"])

frontend_dir = "/home/gbb/landscape-design/trontend"
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
    logger.info(f"Frontend mounted from: {frontend_dir}")
else:
    logger.warning(f"Frontend directory not found: {frontend_dir}")

@app.get("/api")
async def api_root():
    return {"message": "Landscape Design API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
