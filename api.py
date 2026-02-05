from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import tempfile
import os
import json
import re

from gemini_client import analyze_bin_images

app = FastAPI(
    title="Waste Analysis AI API",
    version="1.0"
)


def extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```json|^```|```$", "", text, flags=re.MULTILINE).strip()
    return text


# -------- POST --------
@app.post("/analyze")
async def analyze_bin(
    before_image: UploadFile = File(...),
    after_image: UploadFile = File(...)
):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            before_path = os.path.join(tmpdir, before_image.filename)
            after_path = os.path.join(tmpdir, after_image.filename)

            with open(before_path, "wb") as f:
                f.write(await before_image.read())

            with open(after_path, "wb") as f:
                f.write(await after_image.read())

            output = analyze_bin_images(before_path, after_path)
            clean = extract_json(output)

            return json.loads(clean)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------- GET --------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Waste Analysis AI</title>
    </head>
    <body style="font-family: Arial; padding: 40px">
        <h2>Waste Analysis AI</h2>
        <form action="/analyze" method="post" enctype="multipart/form-data">
            <p>
                <label>Before image:</label><br>
                <input type="file" name="before_image" required>
            </p>
            <p>
                <label>After image:</label><br>
                <input type="file" name="after_image" required>
            </p>
            <button type="submit">Analyze</button>
        </form>
        <p style="margin-top:20px;color:gray">
            Upload two bin images and receive JSON output.
        </p>
    </body>
    </html>
    """

# -------- PUT (placeholder) --------
@app.put("/config")
def update_config(config: dict):
    return {
        "message": "Config endpoint reserved for future use",
        "received": config
    }


# -------- DELETE (placeholder) --------
@app.delete("/reset")
def reset():
    return {"message": "API is stateless – nothing to reset"}
