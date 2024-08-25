import os
from pathlib import Path

import pandas as pd


def get_asset(path):
    asset_path: Path = Path(__file__).parent / "assets" / path
    suffix = asset_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(asset_path)
    else:
        raise NotImplementedError(f"{suffix} assets are not supported.")


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")
