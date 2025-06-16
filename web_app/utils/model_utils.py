from pathlib import Path
from typing import List


def get_available_models(model_dir: str = "models") -> List[str]:
    """Return list of model file names in model_dir."""
    path = Path(model_dir)
    if not path.exists():
        return []
    return [p.name for p in path.iterdir() if p.suffix in {'.pkl', '.joblib', '.h5'}]
