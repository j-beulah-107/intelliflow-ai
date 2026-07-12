import json

import pandas as pd
from pypdf import PdfReader
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer


def extract_pdf_text(file_path: str) -> str:
    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def summarize_csv(file_path: str) -> dict:
    dataframe = pd.read_csv(file_path)

    missing_values = {
        column: int(count)
        for column, count in dataframe.isnull().sum().items()
    }

    data_types = {
        column: str(dtype)
        for column, dtype in dataframe.dtypes.items()
    }

    # Converting through JSON changes NaN into null
    # and NumPy numbers into normal Python numbers.
    sample_data = json.loads(
        dataframe.head(5).to_json(
            orient="records"
        )
    )

    statistics = {}

    if not dataframe.empty:
        statistics = json.loads(
            dataframe.describe(
                include="all"
            ).to_json()
        )

    return {
        "rows": int(dataframe.shape[0]),
        "columns": list(dataframe.columns),
        "shape": [
            int(dataframe.shape[0]),
            int(dataframe.shape[1])
        ],
        "missing_values": missing_values,
        "data_types": data_types,
        "statistics": statistics,
        "sample_data": sample_data
    }


def summarize_text(text: str) -> str:
    if not text.strip():
        return ""

    parser = PlaintextParser.from_string(
        text,
        Tokenizer("english")
    )

    summarizer = LsaSummarizer()

    summary_sentences = summarizer(
        parser.document,
        3
    )

    return " ".join(
        str(sentence)
        for sentence in summary_sentences
    )