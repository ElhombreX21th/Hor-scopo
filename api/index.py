import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("APP_NAME", "SeuFuturo")
os.environ.setdefault("APP_BASE_URL", "https://hypersecit.com.br")
os.environ.setdefault("ALLOWED_ORIGINS", "https://hypersecit.com.br")
os.environ.setdefault("HOROSCOPO_RUNTIME_DIR", "/tmp/seufuturo")

from main import app  # noqa: E402
