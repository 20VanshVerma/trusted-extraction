import json
import base64

from google import genai
from dotenv import load_dotenv

from prompts import EXTRACTION_PROMPT

load_dotenv()

client = genai.Client()


def extract_document(image_bytes, mime_type):
    """
    Send a document image to Gemini and extract structured information.
    """

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=[
            {
                "type": "text",
                "text": EXTRACTION_PROMPT
            },
            {
                "type": "image",
                "data": image_base64,
                "mime_type": mime_type
            }
        ]
    )

    result = interaction.output_text.strip()

    # Remove Markdown code fences if Gemini adds them
    if result.startswith("```json"):
        result = result[7:]

    if result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    result = result.strip()

    try:
        return json.loads(result)

    except json.JSONDecodeError:
        return {
            "error": "Gemini returned invalid JSON",
            "raw_response": result
        }
