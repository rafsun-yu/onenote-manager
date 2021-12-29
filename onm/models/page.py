from datetime import datetime
from os import sep
import pathlib
from bs4 import BeautifulSoup
from .model import Model

class Page(Model):
    """ A OneNote page. """

    def __init__(self, id=None, created_date_time=None, title=None, content_url=None) -> None:
        """
        The attributes are taken from Micrsofot Graph API documentation.
        https://docs.microsoft.com/en-us/graph/api/resources/page?view=graph-rest-1.0
        """
        self.id = id 
        self.created_date_time = created_date_time 
        self.title = title 
        self.content_url = content_url


class PageContent():
    """ Contents of a page """

    def __init__(self, html=None) -> None:
        """
        Instantiates a page. Default content is taken from the template if html is not provided.

        HTML template: see the new-page-template.html.

        Args:
            html (str) - html string of the page. Make sure that the structure is similar
            to the new-page-template.html.
        """
        self.soup = BeautifulSoup(self._get_template_html(), 'html.parser')

        if html is not None:
            self.append(html=html)


    def append(self, separator=None, html=None, page_content=None) -> None:
        """
        Appends provided content to the current content. Either of html or page_content
        must be provided.

        Only the contents inside 'body>div' of the provided page_content is appended to this 'body>div'.

        Args:
            separator (str) - separator is added before appending. 
            html (str) - html string.
            page_content (PageContent)- an instance of PageContent.
        """
        # adds linebreak only when the content is not empty
        if len(self._get_soup_content().contents) != 0:
            self._get_soup_content().append(self.soup.new_tag('br'))

        # adds separator
        if separator is not None:
            self._get_soup_content().append(separator)
            self._get_soup_content().append(self.soup.new_tag('br'))

        # converts page_content to html
        if page_content is not None:
            html = page_content._get_soup_content().encode_contents()

        self._get_soup_content().append(BeautifulSoup(
            html,
            'html.parser'
        ))


    def get_html(self) -> str:
        """
        Returns content as HTML.
        """
        return str(self.soup)


    def get_text(self) -> str:
        """
        Returns content as text.
        """
        return self.soup.get_text()


    def _set_soup_title(self, title:str):
        """ Sets the text of title element (<title>) in the soup object. """
        self.soup.title.string = title


    def _set_soup_created(self, created_timestamp:str=None, created_datetime:datetime=None):
        """ 
        Sets the date created element (<meta name='created'>) in the soup object. 
        Either of the optional argument must be provided.

        Args:
            created_timestamp (str) - Must be in the ISO format.
            created_datetime (datetime) - Created time as datetime instance.
        """
        time_str = created_timestamp if created_timestamp is not None else created_datetime.isoformat()
        created = self.soup.select('meta[name=created]')[0]
        created['content'] = time_str


    def _get_soup_content(self):
        """
        Returns the first 'div' inside 'body' in the soup object. This element is the root
        of the contents. 
        """
        return self.soup.select('body > div')[0]


    def _get_template_html(self):
        """
        Returns template as html from the 'new-page-template.html' file. The file must
        be in the same directory.
        """
        template_file = pathlib.Path(__file__).parent / "new-page-template.html"
        with open(template_file, 'r') as f:
            html_doc = f.read()
        return html_doc
    
