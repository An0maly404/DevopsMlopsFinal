from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from registry import get_production_model

from fastapi.middleware.cors import CORSMiddleware

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge
import time




ml_model = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: runs once, before the server accepts requests
    try:
        ml_model["model"] = get_production_model()
        print("Production model loaded successfully.")
    except Exception as e:
        ml_model["model"] = None
        print(f"!!!!!!!!!!!!!!!!!!Could not load production model: {e}")

    yield
    # Shutdown: nothing to clean up for now
    ml_model.clear()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://*.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

START_TIME = time.time()
uptime_gauge = Gauge("backend_uptime_seconds", "Time since the backend started, in seconds")
uptime_gauge.set_function(lambda: time.time() - START_TIME)

@app.get("/health")
def health():
    return {"status": "ok"}

class HousingFeatures(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float


@app.post("/predict")
def predict(features: HousingFeatures):
    model = ml_model.get("model")
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="No production model available yet."
        )

    input_data = [[
        features.MedInc,
        features.HouseAge,
        features.AveRooms,
        features.AveBedrms,
        features.Population,
        features.AveOccup,
        features.Latitude,
        features.Longitude,
    ]]

    prediction = model.predict(input_data)
    return {"prediction": prediction[0]}