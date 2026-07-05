"""Promote the staging model to production in the MLflow Model Registry."""
import sys

from dotenv import load_dotenv
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient

load_dotenv()

MODEL_NAME = "california-housing-model"
STAGING_ALIAS = "staging"
PRODUCTION_ALIAS = "production"


def main() -> None:
    client = MlflowClient()

    try:
        staging_version = client.get_model_version_by_alias(MODEL_NAME, STAGING_ALIAS)
    except MlflowException:
        print(f"No model '{MODEL_NAME}' with alias '{STAGING_ALIAS}' found — nothing to promote.")
        sys.exit(1)

    client.set_registered_model_alias(
        name=MODEL_NAME,
        alias=PRODUCTION_ALIAS,
        version=staging_version.version,
    )

    print(
        f"Promoted '{MODEL_NAME}' version {staging_version.version} "
        f"from '{STAGING_ALIAS}' to '{PRODUCTION_ALIAS}'."
    )


if __name__ == "__main__":
    main()
