import json
from pathlib import Path

from app.main import app

target = Path("apps/api/openapi.json")
target.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {target}")
