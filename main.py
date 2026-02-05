import json
import re
from gemini_client import analyze_bin_images


def extract_json(text: str) -> str:
    """
    Removes markdown code fences and extracts JSON safely.
    """
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```json|^```|```$", "", text, flags=re.MULTILINE).strip()

    return text


if __name__ == "__main__":
    before_image = "images/before.jpg"
    after_image = "images/after.jpg"

    output = analyze_bin_images(before_image, after_image)

    clean_json = extract_json(output)
    parsed = json.loads(clean_json)

    print(json.dumps(parsed, indent=2))
