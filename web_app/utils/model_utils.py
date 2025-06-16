from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime


def get_available_models(model_dir: str = "models") -> List[str]:
    """Return list of model file names in model_dir.

    The directory is created if it does not exist so the web app can
    accept uploaded models without manual setup.
    """
    path = Path(model_dir)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return [
        p.name
        for p in path.iterdir()
        if p.suffix in {".pkl", ".joblib", ".h5"}
    ]


def get_model_details(model_dir: str = "models") -> List[Dict[str, object]]:
    """Return detailed info for models in model_dir."""
    path = Path(model_dir)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    models = []
    for p in path.iterdir():
        if p.suffix in {".pkl", ".joblib", ".h5"}:
            stat = p.stat()
            models.append({
                "name": p.name,
                "size": round(stat.st_size / 1024, 1),
                "upload_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "type": p.suffix.upper().strip(".")
            })
    return models


def get_history_stats(history_file: str = "downloads/history.json") -> Dict[str, object]:
    """Return run count and last run timestamp from history file."""
    path = Path(history_file)
    if not path.exists():
        return {"run_count": 0, "last_run": None}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"run_count": 0, "last_run": None}
    return {
        "run_count": len(data),
        "last_run": data[-1]["timestamp"] if data else None,
    }
