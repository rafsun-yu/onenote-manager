from os import terminal_size
import re
import click
from datetime import datetime, timedelta
from onm.clients import tools
from onm.clients import config
from onm.models.page import Page, PageContent

@click.group(short_help="performs merge", invoke_without_command=True)
@click.option("--is-365", is_flag=True, default=False, help="whether the user account has 365 sub")
@click.pass_context
def merge(ctx, is_365):
    """ 
    Merges quicknotes of same date into single file. 
    """
    if ctx.invoked_subcommand is not None:
        return

    # Retrieves section names and IDs.
    qn = ctx.obj.pref['merge']['qn']['section_id']
    qnb = ctx.obj.pref['merge']['qnb']['section_id']
    d = ctx.obj.pref['merge']['d']['section_id']
    d_notebook = ctx.obj.pref['merge']['d']['name'].split('/')[0]
    d_section = ctx.obj.pref['merge']['d']['name'].split('/')[1]

    # Gets a list of quicknotes.
    click.echo("Listing quicknotes ...")
    quicknotes = ctx.obj.onc.list_pages(section_id=qn)
    # print(len(quicknotes))

    # Groups quicknotes by creation week.
    groups = group_by_week(quicknotes)

    for week_date, pages in groups.items():
        week_title = week_date.strftime(r"%d-%b-%Y")
        click.echo(f"\nMerge week: {week_title}")

        # Gets or creates the dump page.
        click.echo("\tSearching for dump page ...")

        dump_page = ctx.obj.onc.search(notebook_name=d_notebook, section_name=d_section, page_name=week_title) 

        if dump_page is None:
            click.echo("\tCouldn't find dump page. New one will be created.")
        else:
            click.echo(f"\tFound dump page: {dump_page.title}") 

        # Merges the content from the page group and appends to dump page.
        click.echo("\tMerging pages from the quicknotes ...")

        dump_page_content = PageContent()
        dump_page_content._set_soup_title(week_title)
        dump_page_content._set_soup_created(created_timestamp=str(week_date))

        for page in pages:
            ctx.obj.onc.load_page_content(page)
            dump_page_content.append(separator='===', page_content=page.page_content)

        if dump_page is None:
            dump_page = ctx.obj.onc.create_page (
                section_id=d, 
                title=week_title,
                page_content=dump_page_content
            )
        else:
            ctx.obj.onc.append_to_page(
                page_id=dump_page.id,
                page_content=dump_page_content
            )

        # Moves the pages from the group to backup section.
        click.echo("\tMoving merges pages to backup section ...")
        for page in pages:
            if is_365:
                ctx.obj.onc.copy_page(page_id=page.id, section_id=qnb, move=True)
            else:
                moved_page = ctx.obj.onc.create_page(section_id=qnb, title=page.title, page_content=page.page_content)
                if moved_page is not None:
                    ctx.obj.onc.delete_page(page_id=page.id)

        click.echo("\tDone!")

    click.echo("\nAll notes merged.")


def group_by_week(pages):
    """
    Returns a dictionary <date, list>, where date is a start day of the week (Monday). Each
    date corresponds to a list of pages that are created during that week.

    Args:
        pages - list of Pages.
    """
    pages.sort(key=lambda page: page.created_date_time)
    groups = {}
    for page in pages:
        created = page.created_date_time
        week = (created - timedelta(days=created.weekday())).date()

        if week not in groups.keys():
            groups[week] = []

        groups[week].append(page)

    return groups


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
        