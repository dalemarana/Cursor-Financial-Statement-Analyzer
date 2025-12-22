"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.api.routes import auth

app = FastAPI(
    title="Financial Statement Analyzer API",
    description="Multi-User Bank Statement Processing & Analysis System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

# Import and include other routers
from src.api.routes import transactions, categories, validation, statements, matching
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(validation.router)
app.include_router(statements.router)
app.include_router(matching.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Financial Statement Analyzer API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

