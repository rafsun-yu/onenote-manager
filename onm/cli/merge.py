from os import terminal_size
import click
from onm.clients import tools
from onm.clients import config

@click.group(short_help="performs merge")
@click.pass_context
def merge(ctx):
    """ 
    Merges quicknotes of same date into single file. 
    """
    pass
                   

@merge.command(name='config', short_help='configure merge')
@click.option('-qn', '--quicknote', type=str,  help="location of quicknote")
@click.option('-qnb', '--quicknote-backup', type=str, help="location of quicknote backup")
@click.option('-d', '--dump', type=str, help="location of dump")
@click.option('-st', '--stat', default=False, is_flag=True, help="show current configuration")
@click.pass_context
def config(ctx, quicknote, quicknote_backup, dump, stat):
    """ 
    Prompts user to input location three sections (quicknote, quicknote backup, dump)
    in the format "notebook/section". 

    During merge, pages are looked up in the 'quicknote' section. Then, pages of same date
    are merged into single page in the 'dump' section. The merged pages are then moved to
    the 'quicknote backup' section.
    """
    if stat is True:
        merge_config = ctx.obj.pref['merge']
        qn = f"{merge_config['qn']['notebook']}/{merge_config['qn']['section']}"
        qnb = f"{merge_config['qnb']['notebook']}/{merge_config['qnb']['section']}"
        d = f"{merge_config['d']['notebook']}/{merge_config['d']['section']}"
        click.echo(f"Quicknote: {qn}\nQuicknote Backup: {qnb}\nDump: {d}") 
    else:
        # Check for empty parameter
        if quicknote == '' or quicknote_backup == '' or dump == '':
            click.echo("Some required parameters are empty.")
            return 

        try:
            ctx.obj.pref["merge"]["qn"]["notebook"] = quicknote.split('/')[0]
            ctx.obj.pref["merge"]["qn"]["section"] = quicknote.split('/')[1]
            ctx.obj.pref["merge"]["qnb"]["notebook"] = quicknote_backup.split('/')[0]
            ctx.obj.pref["merge"]["qnb"]["section"] = quicknote_backup.split('/')[1]
            ctx.obj.pref["merge"]["d"]["notebook"] = dump.split('/')[0]
            ctx.obj.pref["merge"]["d"]["section"] = dump.split('/')[1]
        except:
            click.echo("Invalid input.")
            return

        # Verify
        click.echo("Verifying...")

        for key in ctx.obj.pref["merge"].keys():
            section = ctx.obj.onc.search(
                notebook_name=ctx.obj.pref["merge"][key]["notebook"],
                section_name=ctx.obj.pref["merge"][key]["section"]
            )

            if section is None:
                click.echo(f"The location for '{key}' doesn't exist. Try again with different location.")
                return

        click.echo("Verified.")
        tools.save_dict(str(ctx.obj.config.PREF_PATH), ctx.obj.pref)
        