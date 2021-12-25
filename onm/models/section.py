from .model import Model

class Section(Model):
    """ A OneNote section. """

    def __init__(self, id=None, created_date_time=None, display_name=None, pages_url=None):
        """
        The attributes are taken from Micrsofot Graph API documentation.
        https://docs.microsoft.com/en-us/graph/api/notebook-list-sections?view=graph-rest-1.0&tabs=http
        """
        self.id = id 
        self.created_date_time = created_date_time 
        self.display_name = display_name 
        self.pages_url = pages_url 