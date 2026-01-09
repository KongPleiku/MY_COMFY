# src/utils/data.py
import csv
import os
from utils.logger import get_logger

logger = get_logger(__name__)

IMAGE_SRC = "https://picsum.photos/1080/1920"


def load_danbooru_tags(limit=100000):
    """Loads tags from the danbooru.csv file."""
    tags = []
    # Updated path to storage/data/danbooru.csv
    file_path = os.path.join("storage", "data", "danbooru.csv")
    logger.info(f"Loading danbooru tags from {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                if row:
                    # Assuming the tag is in the first column
                    tags.append(row[0])
        logger.info(f"Loaded {len(tags)} tags.")
    except FileNotFoundError:
        logger.error(
            f"Error: {file_path} not found. Please check the directory structure.",
            exc_info=True,
        )
    return tags


ALL_PROMPTS = load_danbooru_tags()
