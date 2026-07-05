"""Train a regression model on the California housing data and log the run to MLflow."""

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

DATA_PATH = Path(__file__).parent.parent / "data" / "raw" / "california_housing.csv"
DVC_POINTER_PATH = DATA_PATH.with_suffix(".csv.dvc")
TARGET_COLUMN = "MedHouseVal"
TEST_SIZE = 0.2
RANDOM_STATE = 42


def get_git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()


def get_dvc_data_version() -> str:
    for line in DVC_POINTER_PATH.read_text().splitlines():
        if "md5:" in line:
            return line.split("md5:")[1].strip()
    return "unknown"


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    mlflow.set_experiment("california-housing")
    with mlflow.start_run():
        model = LinearRegression()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        r2 = r2_score(y_test, predictions)

        mlflow.log_param("model_type", "LinearRegression")
        mlflow.log_param("test_size", TEST_SIZE)
        mlflow.log_param("random_state", RANDOM_STATE)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.set_tag("git_commit", get_git_commit())
        mlflow.set_tag("dvc_data_version", get_dvc_data_version())
        mlflow.sklearn.log_model(model, "model")

        print(f"RMSE: {rmse:.4f}, R2: {r2:.4f}")


if __name__ == "__main__":
    main()
