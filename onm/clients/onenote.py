from datetime import datetime
import pathlib
from bs4 import BeautifulSoup

from .microsoft import MicrosoftClient
from ..models.notebook import Notebook
from ..models.section import Section
from ..models.page import Page

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


    def list_pages(self, section_id: str) -> list:
        """
        Returns a list of all pages inside the provided section.
        """
        pages = []
        data = self.msc.oauth.get(f'https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages').json()

        for o in data['value']:
            p = Page.from_json(json_obj=o)
            pages.append(p)

        return pages


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


    def create_page(self, section_id, title="Untitled page", content_body:str=None) -> Page:
        """
        Creates a new page in the provided section and returns the instance of newly 
        created Page. 

        Args:
            content_body - page content in html or text format
        """
        # Reads template
        template_file = pathlib.Path(__file__).parent / "new-page-template.html"
        with open(template_file, 'r') as f:
            html_doc = f.read()

        soup = BeautifulSoup(html_doc, 'html.parser')

        # Sets title
        soup.title.string = title

        # Sets created datetime
        created = soup.select('meta[name=created]')[0]
        created['content'] = date = datetime.today().isoformat()

        # Sets content
        content = soup.select('body > div')[0]
        if content_body is not None:
            content.append(content_body)

        # Sends post request
        resp = self.msc.oauth.post(
            url = f"https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages",
            data=str(soup),
            headers={
                "Content-Type": "text/html"
            }
        )

        return Page.from_json(json_obj=resp.json())