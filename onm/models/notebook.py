from .model import Model

class Notebook(Model):
    """ A OneNote notebook. """
    
    def __init__(self, id=None, created_date_time=None, display_name=None, sections_url=None):
        """
        The attributes are taken from Micrsofot Graph API documentation.
        https://docs.microsoft.com/en-us/graph/api/onenote-list-notebooks?view=graph-rest-1.0&tabs=http
        """
        self.id = id
        self.created_date_time = created_date_time 
        self.display_name = display_name 
        self.sections_url = sections_url 
