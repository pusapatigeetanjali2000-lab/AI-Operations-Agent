import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-mini")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_ops.db")
APP_ENV = os.getenv("APP_ENV", "development")
