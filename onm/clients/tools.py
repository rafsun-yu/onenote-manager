import platform
import pathlib
import json

def get_datadir() -> pathlib.Path:

    """
    Returns a parent directory path
    where persistent application data can be stored.

    Returns None if OS cannot be resolved.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if platform.system() == "Windows":
        return home / "AppData/Roaming"
    elif platform.system() == "Linux":
        return home / ".local/share"
    elif platform.system() == "Darwin":
        return home / "Library/Application Support"
    else:
        return None


def load_dict(path):
    """
    Loads and returns a JSON file as dictionary.

    Args:
        path (str) - path of the JSON file.
    """
    with open(path, 'r') as f:
        return json.load(f)


def save_dict(path, dict):
    """
    Saves a dictionary a JSON file.

    If file already exists, overwrites.

    Args:
        path (str) - path of the JSON file.
        dict (dict) - dictionary to save.
    """
    with open(path, 'w+') as f:
        json.dump(dict, f)