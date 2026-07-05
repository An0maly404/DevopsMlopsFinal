import mlflow
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "california-housing-model"


def get_production_model():
    return mlflow.sklearn.load_model(f"models:/{MODEL_NAME}@production")
