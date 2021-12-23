from os import terminal_size
import click
from onm.clients import tools

@click.command()
@click.pass_context
@click.option('-p', '--print', 'prnt', default=False, help='Prints the logged in user info.', is_flag=True)
def auth(ctx, prnt):
    # --print
    if prnt:
        if ctx.obj.msc.user is None:
            click.echo("No user is logged in.")
        else:
            click.echo(f"Logged in as: {ctx.obj.msc.user['displayName']} ({ctx.obj.msc.user['userPrincipalName']})")     
                   
    # default (login)
    else:
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
        tools.save_dict(str(ctx.obj.config.USER_INFO_PATH), ctx.obj.msc.user)
        tools.save_dict(str(ctx.obj.config.TOKEN_PATH), ctx.obj.msc.oauth.token)

        # Display success info
        click.echo(f"Logged in as: {ctx.obj.msc.user['displayName']} ({ctx.obj.msc.user['userPrincipalName']})")