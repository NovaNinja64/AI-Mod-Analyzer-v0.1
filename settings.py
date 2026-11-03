import json
from pathlib import Path
import os

CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home())) / "AI Mod Analyzer"
CONFIG_FILE = CONFIG_DIR / "settings.json"

def load_settings():
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"ai_mode": "hybrid"}

def save_settings(settings):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
