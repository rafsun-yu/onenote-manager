import platform
import pathlib
from .tools import *

# Microsoft Graph API configuration -> dict
API = {
    "client_id": "75b896fb-3d25-46d8-a803-b2d793fa3b83",
    "client_secret": "b7N7Q~hBfdvBcolr-4946Do2tte.yQDoqRays",
    "auth_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    "token_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
    "resource_endpoint": "https://graph.microsoft.com/v1.0/me",
    "redirect_uri":"https://login.microsoftonline.com/common/oauth2/nativeclient"
}

# User data directories -> pathlib.Path
DATA_DIR = get_datadir()

if DATA_DIR is None:
    DATA_DIR = ""
    print("Cannot recognize OS. User data may not be saved.")
else:
    DATA_DIR = DATA_DIR / "onenote-manager"


# Access token path
TOKEN_PATH = DATA_DIR / "token.json"

# User info path
USER_INFO_PATH = DATA_DIR / "user.json"

# Preference path
PREF_PATH = DATA_DIR / "preference.json"