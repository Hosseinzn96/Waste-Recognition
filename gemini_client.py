import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from config import GEMINI_API_KEY, MODEL_NAME
from prompts import BIN_ANALYSIS_PROMPT_V2

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)


def analyze_bin_images(before_image_path, after_image_path):
    with open(before_image_path, "rb") as f:
        img_before = f.read()

    with open(after_image_path, "rb") as f:
        img_after = f.read()

    def call_gemini():
        return model.generate_content(
            [
                BIN_ANALYSIS_PROMPT_V2,
                {"mime_type": "image/jpeg", "data": img_before},
                {"mime_type": "image/jpeg", "data": img_after},
            ],
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 1024,
            },
            request_options={"timeout": 60},
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(call_gemini)
            response = future.result(timeout=70)
            return response.text

    except TimeoutError:
        return "Gemini timeout. Please retry."

    except Exception as e:
        return f"Gemini error: {str(e)}"
