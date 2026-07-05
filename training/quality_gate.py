import sys

from dotenv import load_dotenv
from mlflow.tracking import MlflowClient

load_dotenv()

MODEL_NAME = "california-housing-model"
ALIAS = "staging"
RMSE_THRESHOLD = 1.0


def main() -> None:
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else RMSE_THRESHOLD

    client = MlflowClient()
    model_version = client.get_model_version_by_alias(MODEL_NAME, ALIAS)
    run = client.get_run(model_version.run_id)
    rmse = run.data.metrics["rmse"]

    print(f"Candidate model version {model_version.version}: rmse={rmse:.4f} (threshold={threshold})")

    if rmse <= threshold:
        print("PASS")
        sys.exit(0)
    else:
        print("FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
