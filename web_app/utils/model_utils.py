from pathlib import Path
from typing import List


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
