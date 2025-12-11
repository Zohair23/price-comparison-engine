# main.py - this is where the backend starts
# sets up the api server

from dotenv import load_dotenv
load_dotenv()  # Load .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from app.routes import products, prices, alerts, recommendations
from config import settings

# creates all the database tables if they dont exist
Base.metadata.create_all(bind=engine)

# create the fastapi app
app = FastAPI(
    title="Price Comparison API",
    version="0.1.0"
)

# allow frontend to talk to backend (cors)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register all the api routes
app.include_router(products.router)
app.include_router(prices.router)
app.include_router(alerts.router)
app.include_router(recommendations.router)


# just a test endpoint to check if api is running
@app.get("/")
def read_root():
    return {
        "name": "Price Comparison Engine API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# health check - useful for monitoring
@app.get("/health")
def health_check():
    return {"status": "ok"}
