import google.generativeai as genai
import time
from google.api_core import exceptions
from config import GEMINI_API_KEY, MODEL_NAME
from prompts import BIN_ANALYSIS_PROMPT_V2

# 1. Force use of the more stable GRPC transport to avoid "Illegal Metadata"
genai.configure(api_key=GEMINI_API_KEY, transport='grpc') 
model = genai.GenerativeModel(MODEL_NAME)

def analyze_bin_images(before_image_path, after_image_path):
    # Pre-load images to RAM
    with open(before_image_path, "rb") as f:
        img_before = {"mime_type": "image/jpeg", "data": f.read()}
    with open(after_image_path, "rb") as f:
        img_after = {"mime_type": "image/jpeg", "data": f.read()}

    # 2. Retry Logic + Fast Timeout
    for attempt in range(3):
        try:
            # We use a 90s timeout. If Gemini doesn't answer by then, 
            # it's better to tell the user to "Retry" than to hang for 10 mins.
            response = model.generate_content(
                [BIN_ANALYSIS_PROMPT_V2, img_before, img_after],
                generation_config={"temperature": 0.1},
                request_options={"timeout": 90} 
            )
            return response.text

        except (exceptions.ServiceUnavailable, exceptions.InternalServerError) as e:
            # This catches the 503 and 500 errors and retries automatically
            print(f"Server hiccup (Attempt {attempt+1}): {str(e)}")
            time.sleep(2) 
            continue
        except Exception as e:
            return f"Error: {str(e)}"
            
    return "The AI is currently overloaded. Please try again in 10 seconds."

    