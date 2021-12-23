from ..config import API
from ..microsoft import MicrosoftClient
import unittest

msc = MicrosoftClient(
    client_id='',
    client_secret='',
    auth_endpoint='',
    token_endpoint='',
    redirect_uri='',
    scope=["Notes.Read", "User.Read"]
)

class TestMicrosoft(unittest.TestCase):
    
    def test_get_code(self):
        response_uri_1 = "https://login.microsoftonline.com/common/oauth2/nativeclient?code=M.R3_BAY.1ce9c4e7-5e2d-43a2-9ce3-3865c0702889&state=BTo7PQkCcLZh8eIkU6G4WD5mdahoHF"
        self.assertEqual('M.R3_BAY.1ce9c4e7-5e2d-43a2-9ce3-3865c0702889', msc.get_code(response_uri_1))

    def test_fetch_token(self):
        pass

    def test_verify_token(self):
        pass

    def test_load_token(self):
        pass
    
    def test_save_token(self):
        pass

    def test_refresh_token(self):
        pass

    def test_make_request(self):
        pass


if __name__ == '__main__':
    unittest.main()
