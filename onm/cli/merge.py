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
        qn = f"{merge_config['qn']['name']}"
        qnb = f"{merge_config['qnb']['name']}"
        d = f"{merge_config['d']['name']}"
        click.echo(f"Quicknote: {qn}\nQuicknote Backup: {qnb}\nDump: {d}") 
    else:
        # Check for empty parameter
        if any(map(
            lambda x: x is None or x == '', 
            [quicknote, quicknote_backup, dump]
        )):
            click.echo("Some required parameters are empty.")
            return 

        # Verify
        click.echo("Verifying...")

        # this dictionary must have similar structure to pref["merge"] 
        merge_dict = {
            "qn": {"name": quicknote, "section_id": None},
            "qnb": {"name": quicknote_backup, "section_id": None},
            "d": {"name": dump, "section_id": None}
        }

        for key in merge_dict.keys():
            try:
                notebook_name = merge_dict[key]['name'].split('/')[0]
                section_name = merge_dict[key]['name'].split('/')[1]
            except:
                click.echo("Invalid input.")
                return

            section = ctx.obj.onc.search(
                notebook_name=notebook_name,
                section_name=section_name
            )

            if section is None:
                click.echo(f"The location '{merge_dict[key]['name']}' doesn't exist. Try again with different location.")
                return
            else:
                merge_dict[key]['section_id'] = section.id

        click.echo("Verified and saved.")
        ctx.obj.pref['merge'] = merge_dict
        tools.save_dict(str(ctx.obj.config.PREF_PATH), ctx.obj.pref)
        