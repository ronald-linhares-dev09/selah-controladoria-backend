from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

URL_SUPABESE = os.environ.get("URL_SUPABASE")
SERVICE_ROLE_KEY = os.environ.get("SERVICE_ROLE_KEY")

supabase = create_client(supabase_url=URL_SUPABESE, supabase_key=SERVICE_ROLE_KEY)