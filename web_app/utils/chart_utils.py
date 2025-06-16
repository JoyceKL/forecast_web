import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_forecast(dates, actual, predicted, save_path="static/charts/forecast.png"):
    """Plot actual vs predicted values and save to PNG."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.figure(figsize=(10, 4))
    if actual is not None:
        plt.plot(dates, actual, label="Actual")
    plt.plot(dates, predicted, label="Predicted")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
