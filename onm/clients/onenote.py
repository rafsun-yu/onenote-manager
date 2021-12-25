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


    def verify_by_name(self, notebook_name: str, section_name: str = None) -> bool:
        """
        Returns if the provided notebooks/section exists.

        If section_name is missing, then checks if only the notebook exists. If both are provided,
        then checks if the section exists inside the notebook.
        """
        # Verify notebook
        notebooks = self.list_notebooks()

        notebook_id = None
        for notebook in notebooks:
            if notebook.display_name == notebook_name:
                notebook_id = notebook.id

        if notebook_id is None:
            return False
        elif section_name is None:
            return True

        # Verify section
        sections = self.list_sections(notebook_id)

        section_id = None
        for section in sections:
            if section.display_name == section_name:
                section_id = section.id

        return section_id is not None

        
