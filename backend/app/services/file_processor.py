from pypdf import PdfReader
import pandas as pd

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer


def extract_pdf_text(file_path: str):

    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def summarize_csv(file_path: str):

    df = pd.read_csv(file_path)

    return {
        "rows": len(df),
        "columns": list(df.columns),
        "shape": list(df.shape),
        "sample_data": df.head(5).to_dict(
            orient="records"
        )
    }


def summarize_text(text: str):

    parser = PlaintextParser.from_string(
        text,
        Tokenizer("english")
    )

    summarizer = LsaSummarizer()

    summary = summarizer(
        parser.document,
        3
    )

    return " ".join(
        str(sentence)
        for sentence in summary
    )