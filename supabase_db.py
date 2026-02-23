
import os
from supabase import create_client, Client

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)

def load_collection(username: str):
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table("ltb_collections").select("owned_volumes").eq("username", username).execute()
        if response.data:
            return response.data[0]["owned_volumes"]
        return []
    except Exception as e:
        print(f"Supabase Load Error: {e}")
        return []

def save_collection(username: str, owned_volumes: list):
    client = get_supabase_client()
    if not client:
        return
    
    try:
        # Upsert: Update if exists, insert if not
        data = {
            "username": username,
            "owned_volumes": owned_volumes
        }
        client.table("ltb_collections").upsert(data, on_conflict="username").execute()
    except Exception as e:
        print(f"Supabase Save Error: {e}")
