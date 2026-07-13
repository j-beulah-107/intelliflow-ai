from pathlib import Path
from uuid import uuid4

import matplotlib.pyplot as plt
import pandas as pd


CHART_DIRECTORY = Path("generated_charts")


def generate_csv_charts(file_path: str) -> list[dict]:
    dataframe = pd.read_csv(file_path)
    CHART_DIRECTORY.mkdir(parents=True, exist_ok=True)

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns.tolist()

    charts: list[dict] = []

    for column in numeric_columns[:3]:
        clean_data = dataframe[column].dropna()

        if clean_data.empty:
            continue

        stored_name = f"{uuid4().hex}.png"
        chart_path = CHART_DIRECTORY / stored_name

        plt.figure()
        clean_data.plot(
            kind="hist",
            title=f"Distribution of {column}"
        )
        plt.xlabel(column)
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        charts.append(
            {
                "column": column,
                "chart_type": "histogram",
                "stored_name": stored_name,
                "chart_path": str(chart_path),
            }
        )

    return charts