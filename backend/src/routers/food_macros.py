from fastapi import APIRouter, UploadFile, File, Depends
import os, datetime, time, base64, re, json, ast, requests
from dotenv import load_dotenv
import openai
import aiofiles
from db import get_connection
from routers.auth import get_current_user

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()
LOG_PATH = "openai_requests.log"

def log_openai_file(prompt, ai_response, response_time_ms):
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n---\n[{timestamp}]\n")
        f.write(f"PROMPT:\n{prompt}\n\n")
        f.write(f"AI RESPONSE ({response_time_ms} ms):\n{ai_response}\n")

def log_openai_db(prompt, ai_response, response_time_ms):
    conn = get_connection()
    cur = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cur.execute(
        "INSERT INTO openai_logs (timestamp, prompt, response, response_time_ms) VALUES (?, ?, ?, ?)",
        (timestamp, prompt, ai_response, response_time_ms)
    )
    conn.commit()
    conn.close()

def get_macros_from_openfoodfacts(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}"
    try:
        r = requests.get(url, timeout=4)
        data = r.json()
        if 'product' in data and 'nutriments' in data['product']:
            n = data['product']['nutriments']
            return {
                "description": data['product'].get('product_name', f"Product {barcode}"),
                "protein": n.get('proteins_100g'),
                "carbs": n.get('carbohydrates_100g'),
                "fat": n.get('fat_100g'),
                "calories": n.get('energy-kcal_100g'),
                "barcode": barcode
            }
    except Exception as e:
        print(f"OpenFoodFacts error: {e}")
    return None

@router.post("/estimate-macro")
async def estimate_macro(image: UploadFile = File(...), user=Depends(get_current_user)):
    temp_filename = f"temp_{image.filename}"
    async with aiofiles.open(temp_filename, 'wb') as out_file:
        content = await image.read()
        await out_file.write(content)
    with open(temp_filename, "rb") as f:
        img_data = f.read()
    os.remove(temp_filename)
    base64_img = base64.b64encode(img_data).decode()
    data_url = f"data:image/jpeg;base64,{base64_img}"

    prompt = """
Recognize what is shown in the photo (recipe, barcode, or food dish).
If a barcode is visible, extract its number and return only the barcode in the JSON response. Do not estimate macros for barcoded products. If no barcode is present, estimate macronutrients as best as possible.
Respond in strict JSON format:
{
  "barcode": "if detected, else null",
  "description": "what is shown in the photo",
  "base_amount": 100,
  "unit": "g",
  "protein": null or value,
  "carbs": null or value,
  "fat": null or value,
  "calories": null or value
}
Use only double quotes for all keys and values. If a barcode is found, set protein, carbs, fat, and calories to null.
"""
    # --- Call GPT
    start_time = time.time()
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]}
        ]
    )
    response_time_ms = int((time.time() - start_time) * 1000)
    answer = response.choices[0].message.content

    log_openai_file(prompt + "\n[IMG: ...]", answer, response_time_ms)
    log_openai_db(prompt + "\n[IMG: ...]", answer, response_time_ms)

    # Parse GPT response
    match = re.search(r"\{[\s\S]*\}", answer)
    if match:
        raw_json = match.group()
        try:
            macros = json.loads(raw_json)
        except Exception:
            try:
                macros = ast.literal_eval(raw_json)
            except Exception:
                macros = {"error": f"Could not parse JSON from GPT.", "raw": raw_json}
    else:
        macros = {"error": f"No JSON in GPT answer.", "raw": answer}

    # If barcode, try Open Food Facts
    if macros.get("barcode"):
        product = get_macros_from_openfoodfacts(macros["barcode"])
        if product and product["protein"] is not None:
            return product
        # If not found, return info for user:
        macros["note"] = "Barcode detected but not found in Open Food Facts."
    return macros

@router.get("/openai-logs")
def get_openai_logs(limit: int = 20, user=Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM openai_logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [
        {"id": r[0], "timestamp": r[1], "prompt": r[2], "response": r[3], "response_time_ms": r[4]}
        for r in rows
    ]
