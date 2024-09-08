import os

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
