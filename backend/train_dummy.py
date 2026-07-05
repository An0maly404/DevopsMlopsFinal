from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
import joblib
import os


def main():
    # Loading of the dataset
    data = fetch_california_housing()
    X, y = data.data, data.target

    # Test model
    model = LinearRegression()
    model.fit(X, y)

    out_dir = os.path.join(os.path.dirname(__file__), '')
    out_path = os.path.join(out_dir, 'dummy_model.joblib')

    joblib.dump(model, out_path)
    print(f"Model saved to: {out_path}")


if __name__ == '__main__':
    main()
