from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from typing import List


app = FastAPI()


@app.get("/health")
def health_check():
	return {"status": "alive"}


class HousingFeatures(BaseModel):
	median_income: float
	house_age: float
	avg_rooms: float
	avg_bedrooms: float
	population: float
	avg_occupancy: float
	latitude: float
	longitude: float


@app.post("/predict")
def predict(features: HousingFeatures):
	# EXPECT THE FILE "dummy_model.joblib" TO BE IN THE SAME DIRECTORY AS THIS SCRIPT !!
	model = joblib.load("dummy_model.joblib")
	vals: List[float] = [
		features.median_income,
		features.house_age,
		features.avg_rooms,
		features.avg_bedrooms,
		features.population,
		features.avg_occupancy,
		features.latitude,
		features.longitude,
	]
	pred = model.predict([vals])[0]
	return {"prediction": float(pred)}
