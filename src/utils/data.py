# src/utils/data.py
import csv
import os

IMAGE_SRC = "https://picsum.photos/1080/1920"


def load_danbooru_tags(limit=100000):
    """Loads tags from the danbooru.csv file."""
    tags = []
    file_path = os.path.join("json", "danbooru.csv")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                if row:
                    tags.append(row[0])
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    return tags


ALL_PROMPTS = load_danbooru_tags()
