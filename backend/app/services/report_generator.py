def generate_csv_report(summary: dict) -> str:
    rows = summary.get("rows", 0)
    columns = summary.get("columns", [])
    missing_values = summary.get("missing_values", {})

    missing_columns = [
        column
        for column, count in missing_values.items()
        if count > 0
    ]

    report_parts = [
        f"The dataset contains {rows} rows and {len(columns)} columns.",
        f"The available columns are: {', '.join(columns)}."
    ]

    if missing_columns:
        report_parts.append(
            "Missing values were found in: "
            + ", ".join(missing_columns)
            + "."
        )
    else:
        report_parts.append(
            "No missing values were detected."
        )

    return " ".join(report_parts)