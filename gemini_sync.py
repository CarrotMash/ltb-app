
import os
from google import genai
from google.genai import types

def get_ai_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def fetch_missing_titles(volume_nrs):
    client = get_ai_client()
    if not client or not volume_nrs:
        return []
    
    prompt = f"Nenne mir die offiziellen Buchtitel der folgenden Lustigen Taschenbücher (LTB): {', '.join(map(str, volume_nrs))}. Antworte NUR im JSON Format: [{{'nr': 1, 'title': '...'}}, ...]"
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        import json
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Sync Error: {e}")
        return []

def fetch_latest_volumes(current_max):
    client = get_ai_client()
    if not client:
        return []
    
    prompt = f"Welche LTB Bände sind nach Band {current_max} erschienen oder angekündigt? Nenne mir Nummer, Titel und Erscheinungsdatum. Antworte NUR im JSON Format: [{{'nr': 609, 'title': '...', 'release_date': 'YYYY-MM-DD'}}, ...]"
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        import json
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Search Error: {e}")
        return []
