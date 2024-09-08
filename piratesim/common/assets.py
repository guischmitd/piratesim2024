from pathlib import Path

import pandas as pd


def get_asset(path):
    asset_path: Path = Path(__file__).parents[1] / "assets" / path
    suffix = asset_path.suffix.lower()
    if suffix.lower() == ".csv":
        try:
            output = pd.read_csv(asset_path, sep=";")
        except:
            output = pd.read_csv(asset_path)
        return output
    else:
        raise NotImplementedError(f"{suffix} assets are not supported.")
