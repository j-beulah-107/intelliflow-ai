from pathlib import Path

import pandas as pd


def clean_csv(file_path: str) -> dict:
    dataframe = pd.read_csv(file_path)

    original_rows = int(dataframe.shape[0])
    original_columns = int(dataframe.shape[1])

    duplicate_rows = int(dataframe.duplicated().sum())

    dataframe = dataframe.drop_duplicates()

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    text_columns = dataframe.select_dtypes(
        include="object"
    ).columns

    for column in numeric_columns:
        if dataframe[column].isnull().any():
            dataframe[column] = dataframe[column].fillna(
                dataframe[column].median()
            )

    for column in text_columns:
        if dataframe[column].isnull().any():
            dataframe[column] = dataframe[column].fillna(
                "Unknown"
            )

    source_path = Path(file_path)
    cleaned_name = (
        f"{source_path.stem}_cleaned"
        f"{source_path.suffix}"
    )
    cleaned_path = source_path.parent / cleaned_name

    dataframe.to_csv(
        cleaned_path,
        index=False
    )

    return {
        "message": "CSV cleaned successfully",
        "original_rows": original_rows,
        "cleaned_rows": int(dataframe.shape[0]),
        "columns": original_columns,
        "duplicates_removed": duplicate_rows,
        "cleaned_file_path": str(cleaned_path),
    }