"""Fetch the California housing dataset and save it as a CSV for DVC tracking."""

from pathlib import Path

from sklearn.datasets import fetch_california_housing

OUTPUT_PATH = Path(__file__).parent / "raw" / "california_housing.csv"


def main() -> None:
    frame = fetch_california_housing(as_frame=True).frame
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(frame)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
