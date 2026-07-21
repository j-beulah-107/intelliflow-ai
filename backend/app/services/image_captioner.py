from functools import lru_cache
from pathlib import Path

import torch
from PIL import Image, UnidentifiedImageError
from transformers import BlipForConditionalGeneration, BlipProcessor


MODEL_NAME = "Salesforce/blip-image-captioning-base"


@lru_cache(maxsize=1)
def load_captioning_model():
    """
    Load and cache the BLIP processor and model.

    The model is downloaded during the first request and then reused
    for later image-captioning requests.
    """
    processor = BlipProcessor.from_pretrained(MODEL_NAME)

    model = BlipForConditionalGeneration.from_pretrained(
        MODEL_NAME
    )

    model.eval()

    return processor, model


def generate_image_caption(file_path: Path) -> str:
    """
    Generate a natural-language description for an image.
    """
    try:
        with Image.open(file_path) as image:
            rgb_image = image.convert("RGB")

    except UnidentifiedImageError as exc:
        raise ValueError(
            "The uploaded image could not be read."
        ) from exc

    except OSError as exc:
        raise ValueError(
            "The uploaded image appears to be damaged."
        ) from exc

    processor, model = load_captioning_model()

    inputs = processor(
        images=rgb_image,
        return_tensors="pt",
    )

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=40,
            num_beams=4,
        )

    caption = processor.decode(
        output_ids[0],
        skip_special_tokens=True,
    ).strip()

    if not caption:
        return "No AI description could be generated."

    return caption