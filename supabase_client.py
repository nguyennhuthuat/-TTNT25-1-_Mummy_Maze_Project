import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from your.env file
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Create a single, reusable Supabase client instance
supabase: Client = create_client(url, key)