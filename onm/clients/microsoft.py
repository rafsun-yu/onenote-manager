from requests_oauthlib import OAuth2Session
from urllib.parse import urlparse, parse_qs

class MicrosoftClient:
    def __init__(self, client_id, client_secret, auth_endpoint, token_endpoint, scope, redirect_uri):
        """
        This class is responsible for user authorization (oauth2) management
        and setting up requests.

        Args:
            scope = It is a list of scopes.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_endpoint = auth_endpoint
        self.token_endpoint = token_endpoint
        self.scope = " ".join(scope)
        self.redirect_uri = redirect_uri

        self.oauth = OAuth2Session(
            client_id = self.client_id,
            redirect_uri = self.redirect_uri,
            scope = self.scope
        )
        self.user = None 


    def get_auth_url(self):
        """
        Generates and returns the authentication url required to get the authentication code. 
        """
        auth_url, state = self.oauth.authorization_url(self.auth_endpoint)
        return auth_url

    
    def get_code(self, response_uri):
        """
        Parses and returns the 'code' parameter from the redirected uri.
        
        Exceptions:
            AuthError - Authorization fails. \n
            MissingParamError - 'code' parameter is missing from the uri.
        """
        query_string = urlparse(response_uri).query
        query = parse_qs(query_string)

        # Check of authorization error
        if 'error' in query.keys():
            raise Exception(query["error_description"][0])

        # Check if format is okay
        if 'code' not in query.keys():
            raise Exception("The parameter 'code' is missing.")
        
        return query["code"][0]


    def fetch_token(self, code):
        """
        Fetches access token using the provided code. 
        """
        self.oauth.fetch_token(
            token_url = self.token_endpoint,
            code = code,
            method = "POST",
            include_client_id = True
        ) 


    def fetch_user(self):
        """
        Fetches user's full name and email.

        Raises exception if no token has been loaded prior to this call.
        """
        response = self.oauth.get("https://graph.microsoft.com/v1.0/me")
        self.user = response.json()



    def verify_token():
        """
        Returns whether the current token is valid.
        """
        pass


    def refresh_token():
        """
        Refreshes expired token.
        """
        pass 


    def make_request(self):
        """
        Returns a session object.
        """
        self.oauth.request()
        pass 
    
# class MissingParamError(Exception):
#     """ Rasied when the response_uri passed to the get_code method is invalid """
#     pass 

# class AuthError(Exception):
#     """ Raised when the authorization fails """
#     pass 