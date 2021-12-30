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

        Except for page_content.
        """
        self.id = id 
        self.created_date_time = created_date_time 
        self.title = title 
        self.content_url = content_url
        self.page_content = PageContent()


class PageContent():
    """ Contents of a page """

    def __init__(self, html=None, html_body=None) -> None:
        """
        Instantiates a page's content. 
        
        Default content is taken from the template if neither html nor html_body is provided.

        HTML template: see the new-page-template.html.

        Args:
            html (str) - entire html string of page. See the HTML template.
            html_body (str) - html string of the page's body.
        """
        if html is not None:
            self.soup = BeautifulSoup(html, 'html.parser')
            return
        else:    
            self.soup = BeautifulSoup(self._get_template_html(), 'html.parser')

            if html_body is not None:
                self.append(html_body=html_body)


    def append(self, separator=None, html_body=None, page_content=None) -> None:
        """
        Appends provided content to the current content. Either of html_body or page_content
        must be provided.

        Only the contents inside 'body>div' of the provided page_content is appended to this 'body>div'.

        Args:
            separator (str) - separator is added before appending. 
            html_body (str) - html string to be appened in the body.
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
            html_body = page_content._get_soup_content().encode_contents()

        self._get_soup_content().append(BeautifulSoup(
            html_body,
            'html.parser'
        ))


    def get_html(self, only_body=False) -> str:
        """
        Returns entire page content as HTML.

        Args:
            only_body - If set, then returns only HTML inside the first 'body > div'.
        """
        if only_body:
            return self._get_soup_content().encode_contents().decode("utf-8")
        else:
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
    
