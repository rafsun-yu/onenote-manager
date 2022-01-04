from datetime import datetime
import pathlib
import json
from bs4 import BeautifulSoup
import polling

from .microsoft import MicrosoftClient
from ..models.notebook import Notebook
from ..models.section import Section
from ..models.page import Page, PageContent

class OneNoteClient:
    """
    Manages all API calls specific to OneNote.
    """

    def __init__(self, msc: MicrosoftClient):
        """
        Args:
            msc (MicrosoftClient) - An instance of microsoft.MicrosoftClient.
        """
        self.msc = msc
        pass


    def list_notebooks(self) -> list:
        """
        Returns a list of all notebooks.
        """
        notebooks = []
        data = self.msc.oauth.get('https://graph.microsoft.com/v1.0/me/onenote/notebooks').json()

        for o in data['value']:
            n = Notebook.from_json(json_obj=o)
            notebooks.append(n)

        return notebooks


    def list_sections(self, notebook_id: str) -> list:
        """
        Returns a list of all sections inside the provided notebook.
        """
        sections = []
        data = self.msc.oauth.get(f'https://graph.microsoft.com/v1.0/me/onenote/notebooks/{notebook_id}/sections').json()

        for o in data['value']:
            s = Section.from_json(json_obj=o)
            sections.append(s)

        return sections


    def list_pages(self, section_id:str=None, url:str=None) -> list:
        """
        Returns a list of all pages inside the provided section or url.
        """
        if section_id is not None:
            url = f'https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages'

        pages = []
        data = self.msc.oauth.get(url).json()

        for o in data['value']:
            p = Page.from_json(json_obj=o)
            pages.append(p)

        next_page_url = None
        if '@odata.nextLink' in data.keys():
            next_page_url = data['@odata.nextLink']

        if next_page_url is None:
            return pages
        else:
            return pages + self.list_pages(url=next_page_url)


    def search(self, notebook_name: str, section_name: str = None, page_name: str = None):
        """
        Returns the first matching instance from the search criteria. If nothing matches, 
        returns None.

        If only notebook_name is provided, then only searches for notebook_name. \n
        If only notebook_name and section_name are provided, then searches for section_name 
        inside the notebook_name. \n
        If all three argumetns are provided, then searches for page_name inside section_name
        inside notebook_name.

        Returns:
            Notebook | Section | Page | None
        """
        # Search notebook
        notebooks = self.list_notebooks()
        notebook = self._search_list(notebooks, lambda x : x.display_name == notebook_name)

        if notebook is None:
            return None
        elif section_name is None:
            return notebook

        # Search section
        sections = self.list_sections(notebook.id)
        section = self._search_list(sections, lambda x : x.display_name == section_name)

        if section is None:
            return None
        elif page_name is None:
            return section

        # Search page
        pages = self.list_pages(section.id)
        page = self._search_list(pages, lambda x : x.title == page_name)

        return page

        
    def _search_list(self, l: list, condition):
        """
        Returns the first item in the list that matches the condition. If none matches,
        returns None.

        Args:
            l - list \n
            condition - a lambda or a function that takes on argument (a list item) and returns bool.
        """
        return next(
            filter(condition, l),
            None
        )


    def create_page(self, section_id, title="Untitled page", content_body:str=None, page_content:PageContent=None) -> Page:
        """
        Creates a new page in the provided section and returns the instance of newly 
        created Page. 

        Args:
            content_body - page content in html or text format
            page_content - an instance of PageContent
        """
        if page_content is None:
            page_content = PageContent(html_body=content_body)

        page_content._set_soup_created(created_datetime=datetime.today())
        page_content._set_soup_title(title=title)

        # Sends post request
        resp = self.msc.oauth.post(
            url = f"https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages",
            data=page_content.get_html().encode('utf-8'),
            headers={
                "Content-Type": "text/html"
            }
        )

        return Page.from_json(json_obj=resp.json())


    def load_page_content(self, page:Page):
        """
        Loads content as PageContent for the provided page and set it to the page_content
        attribute.
        """
        html = self.msc.oauth.get(page.content_url).text
        page.page_content = PageContent(html=html)


    def append_to_page(self, page_id:str, html_body:str=None, page_content:PageContent=None) -> None:
        """
        Appends the provided content to the page with page_id. Either of html_body or
        page_content must be provided.
        """
        if html_body is None:
            html_body = page_content.get_html(only_body=True)

        resp = self.msc.oauth.patch(
            url=f"https://graph.microsoft.com/v1.0//me/onenote/pages/{page_id}/content",
            data = json.dumps([{
                'target': 'body',
                'action': 'append',
                'content': html_body
            }]),
            headers={
                "Content-Type": "application/json"
            }
        )

    
    def copy_page(self, page_id:str, section_id:str, move:bool=False) -> None:
        """
        Copy a page to a section. 

        Args:
            page_id - ID of the page to be copied.
            section_id - ID of the destination section.
            move - If True, removes the page if copy is successful.  
        """
        # Requests copy operation
        resp = self.msc.oauth.post(
            url=f"https://graph.microsoft.com/v1.0//me/onenote/pages/{page_id}/copyToSection",
            data=json.dumps({
                'id': section_id
            }),
            headers={
                "Content-Type": "application/json"
            }
        )

        if resp.status_code != 202:
            print(resp.text)
            return

        # Creates polling to check result of the operation
        operation_id = resp.json()['id']

        def polling_status(resp):
            if resp.status_code == 200:
                return resp.json()['status'].lower()  
            else: 
                return None

        try:
            polling_result = polling.poll(
                lambda: self.msc.oauth.get(
                    url=f"https://graph.microsoft.com/v1.0/me/onenote/operations/{operation_id}"
                ),
                step=10,
                max_tries=3,
                check_success=lambda resp: polling_status(resp) in ['completed', 'failed']
            )
        except polling.MaxCallException as e:
            pass

        if polling_status(polling_result) != 'completed':
            # print(polling_result)
            return

        # Perform move operation
        if move:
            self.delete_page(page_id=page_id)


    def delete_page(self, page_id:str):
        """
        Deletes a page.

        Args:
            page_id - ID of the page to be deleted.
        """
        resp = self.msc.oauth.delete(
            url=f"https://graph.microsoft.com/v1.0//me/onenote/pages/{page_id}"
        )