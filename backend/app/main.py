import time
from fastapi import FastAPI, Depends, status, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from app.core.config import settings
from app.db.session import get_db, engine, Base
from app.api.endpoints import router as api_router

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Latency in seconds",
    ["method", "endpoint"],
)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LabTrack API - Shared lab equipment and inventory tracking",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    endpoint = request.url.path
    # Group item and checkout IDs in path to keep metrics cardinality clean
    if endpoint.startswith("/api/items/") and len(endpoint.split("/")) >= 4:
        parts = endpoint.split("/")
        # /api/items/{id} or /api/items/{id}/checkouts
        if len(parts) == 4 and parts[3].isdigit():
            endpoint = "/api/items/{id}"
        elif len(parts) == 5 and parts[3].isdigit():
            endpoint = f"/api/items/{{id}}/{parts[4]}"
    elif endpoint.startswith("/api/checkouts/") and len(endpoint.split("/")) >= 4:
        parts = endpoint.split("/")
        if len(parts) == 5 and parts[3].isdigit():
            endpoint = f"/api/checkouts/{{id}}/{parts[4]}"

    REQUEST_COUNT.labels(
        method=request.method, endpoint=endpoint, status_code=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration)
    return response


# Root info endpoint
@app.get("/", tags=["Info"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "docs": "/docs",
    }


# Health check (Liveness - lightweight, does NOT depend on DB)
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": settings.PROJECT_NAME}


# Readiness check (Readiness - verifies DB connectivity)
@app.get("/ready", tags=["Health"])
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return Response(
            content='{"status": "not ready", "database": "unavailable"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
        )


# Prometheus metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Include API routes under /api
app.include_router(api_router, prefix=settings.API_PREFIX)
