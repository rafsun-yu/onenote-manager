from os import terminal_size
import click
from onm.clients import tools

@click.group()
@click.pass_context
def auth(ctx):
    pass 


@auth.command(name="st", short_help="login status")
@click.pass_context
def status(ctx):
    """Prints the current logged in user."""
    if ctx.obj.msc.user is None:
        click.echo("No user is logged in.")
    else:
        click.echo(f"Logged in as: {ctx.obj.msc.user['displayName']} ({ctx.obj.msc.user['userPrincipalName']})")     
                   

@auth.command(name="li", short_help="log in")
@click.pass_context
def login(ctx):
    """Prompts login."""

    # Check if already logged in
    if ctx.obj.msc.user is not None and \
        not click.confirm('Do you want to remove current user first, and then log in?'):
            return

    # Fetch token
    click.echo("Go to this URL, copy and paste the final redirected uri below.")
    click.echo(f"\n{ctx.obj.msc.get_auth_url()}\n")
    response_uri = click.prompt("Paste here")
    code = ctx.obj.msc.get_code(response_uri)

    click.echo("Logging in...")
    ctx.obj.msc.fetch_token(code)

    # Fetch user
    ctx.obj.msc.fetch_user()

    # Save user and token 
    ctx.invoke(logout)
    tools.save_dict(str(ctx.obj.config.USER_INFO_PATH), ctx.obj.msc.user)
    tools.save_dict(str(ctx.obj.config.TOKEN_PATH), ctx.obj.msc.oauth.token)

    # Display success info
    click.echo(f"Logged in as: {ctx.obj.msc.user['displayName']} ({ctx.obj.msc.user['userPrincipalName']})")


@auth.command(name="lo", short_help="log out")
@click.pass_context
def logout(ctx):
    """Clears user information from local storage."""
    ctx.obj.config.TOKEN_PATH.unlink(missing_ok=True)
    ctx.obj.config.USER_INFO_PATH.unlink(missing_ok=True)
    pass