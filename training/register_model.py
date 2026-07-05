import sys

import mlflow
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

EXPERIMENT_NAME = "california-housing"
MODEL_NAME = "california-housing-model"


def main() -> None:
    client = MlflowClient()
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)

    best_run_summary = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.rmse ASC"],
        max_results=1,
    )[0]
    best_run = client.get_run(best_run_summary.info.run_id)
    print(f"Best run: {best_run.info.run_id} (rmse={best_run.data.metrics['rmse']:.4f})")

    model_id = best_run.outputs.model_outputs[0].model_id
    model_uri = client.get_logged_model(model_id).model_uri
    result = mlflow.register_model(model_uri, MODEL_NAME)

    client.set_registered_model_alias(
        name=MODEL_NAME,
        alias="staging",
        version=result.version,
    )
    print(f"Registered '{MODEL_NAME}' version {result.version} and aliased it as staging")


if __name__ == "__main__":
    main()
