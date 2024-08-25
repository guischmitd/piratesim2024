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


def in_notebook():
    try:
        from IPython import get_ipython

        if "IPKernelApp" not in get_ipython().config:
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


def clear_terminal():
    if in_notebook():
        from IPython.display import clear_output

        clear_output(wait=True)
    else:
        os.system("cls" if os.name == "nt" else "clear")
