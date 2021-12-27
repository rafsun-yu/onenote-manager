import click

from onm.clients.onenote import OneNoteClient
from .auth import auth
from .merge import merge
from onm.clients import config
from onm.clients import tools
from onm.clients.microsoft import MicrosoftClient

@click.group()
@click.pass_context
def launch(ctx):
    """
    Entry point of the CLI.
    """

    # Configuration object
    ctx.obj.config = config

    # Initiates Microsoft Client
    ctx.obj.msc = MicrosoftClient(
        client_id=config.API["client_id"],
        client_secret=config.API["client_secret"],
        auth_endpoint=config.API["auth_endpoint"],
        token_endpoint=config.API["token_endpoint"],
        redirect_uri=config.API["redirect_uri"],
        scope=["Notes.Read", "User.Read"]
    )

    # Initates OneNote Client
    ctx.obj.onc = OneNoteClient(ctx.obj.msc)

    # Loads user and token in MSC from local storage
    config.DATA_DIR.mkdir(exist_ok=True, parents=True)

    if config.TOKEN_PATH.is_file() and config.USER_INFO_PATH.is_file():
        ctx.obj.msc.oauth.token = tools.load_dict(config.TOKEN_PATH)
        ctx.obj.msc.user = tools.load_dict(config.USER_INFO_PATH)

    
    # Default user preference
    ctx.obj.pref = {
        "merge": {
            "qn": {"name": None, "section_id": None},
            "qnb": {"name": None, "section_id": None},
            "d": {"name": None, "section_id": None}
        }
    }

    # Load user preference
    if config.PREF_PATH.is_file():
        ctx.obj.pref = tools.load_dict(config.PREF_PATH)



# Adds subcommands
launch.add_command(auth)
launch.add_command(merge)
