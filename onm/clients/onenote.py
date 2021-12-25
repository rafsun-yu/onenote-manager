from ..models.notebook import Notebook
from ..models.section import Section
from .microsoft import MicrosoftClient
import json

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


    def search(self, notebook_name: str, section_name: str = None):
        """
        Returns the first matching instance from the search criteria. If nothing matches, 
        returns None.

        If section_name is None, then only searches for notebook_name. If both are provided,
        then searches for section_name inside the notebook_name.

        Returns:
            Notebook | Section | None
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

        return section

        
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