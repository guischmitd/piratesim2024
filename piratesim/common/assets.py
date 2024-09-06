from pathlib import Path

import pandas as pd


def get_asset(path):
    asset_path: Path = Path(__file__).parents[1] / "assets" / path
    suffix = asset_path.suffix.lower()
    if suffix.lower() == ".csv":
        return pd.read_csv(asset_path)
    else:
        raise NotImplementedError(f"{suffix} assets are not supported.")
