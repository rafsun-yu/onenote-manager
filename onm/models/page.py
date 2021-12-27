from .model import Model

class Page(Model):
    """ A OneNote page. """

    def __init__(self, id=None, created_date_time=None, title=None, content_url=None):
        """
        The attributes are taken from Micrsofot Graph API documentation.
        https://docs.microsoft.com/en-us/graph/api/resources/page?view=graph-rest-1.0
        """
        self.id = id 
        self.created_date_time = created_date_time 
        self.title = title 
        self.content_url = content_url