import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE")
SUPABASE_QUERY_NAME = os.getenv("SUPABASE_QUERY_NAME")

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
