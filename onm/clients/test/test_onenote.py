from urllib import parse
from onm.clients import config
from onm.clients import tools
from ..microsoft import MicrosoftClient
from ..onenote import OneNoteClient
import unittest
import pathlib

# Parent path 
parent_path = pathlib.Path(__file__).parent

# OneNoteClient
msc = MicrosoftClient(
    client_id=config.API["client_id"],
    client_secret=config.API["client_secret"],
    auth_endpoint=config.API["auth_endpoint"],
    token_endpoint=config.API["token_endpoint"],
    redirect_uri=config.API["redirect_uri"],
    scope=["Notes.Read", "User.Read", "Files.Read"]
)

msc.oauth.token = tools.load_dict(str(parent_path / 'data/token.json'))
onc = OneNoteClient(msc)


class TestOneNote(unittest.TestCase):
    """
    Note: this test uses test data from the account rafsun82@wst7f.onmicrosoft.com. To run
    tests successfully, set access_token for the account in MicrosoftClient.
    """

    def test_list_notebooks(self):
        notebooks = onc.list_notebooks()
        names = list(map(lambda n: n.display_name, notebooks))
        expected_names = ['School', 'My Work']
        self.assertEqual(names.sort(), expected_names.sort())


    def test_list_sections(self):
        sections = onc.list_sections('1-e2faea24-c18e-4e5b-b9e7-59f9dedd9621')
        names = list(map(lambda s: s.display_name, sections))
        expected_names = ['Deadlines', 'Classnotes']
        self.assertEqual(names.sort(), expected_names.sort())
    

    def test_verify_notebook(self):
        self.assertTrue(onc.verify_by_name('School'))
        self.assertFalse(onc.verify_by_name('Home'))
        pass 

    def test_verify_section(self):
        self.assertTrue(onc.verify_by_name('School', section_name='Deadlines'))
        self.assertFalse(onc.verify_by_name('My Work', section_name='Deadlines'))
        pass 


if __name__ == '__main__':
    unittest.main()
