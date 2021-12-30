from os import sep
from urllib import parse
from onm.clients import config
from onm.clients import tools
from onm.models.page import Page, PageContent
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


    def test_list_pages(self):
        pages = onc.list_pages('1-420c410c-927c-4e5f-b082-025e444b88e8')
        names = list(map(lambda p: p.title, pages))
        expected_names = ['First page', 'Notes on meeting x', 'Reminder about report y']
        self.assertEqual(names.sort(), expected_names.sort())
    

    def test_verify_notebook(self):
        self.assertIsNotNone(onc.search('School'))
        self.assertIsNone(onc.search('Home')) 


    def test_verify_section(self):
        self.assertIsNotNone(onc.search('School', section_name='Deadlines'))
        self.assertIsNone(onc.search('My Work', section_name='Deadlines'))


    def test_verify_page(self):
        self.assertIsNotNone(onc.search('My Work', section_name='Untitled Section', page_name='Notes on meeting x'))
        self.assertIsNone(onc.search('My Work', section_name='Quick Notex', page_name='Notes on meeting x'))
        self.assertIsNone(onc.search('My Work', section_name='Quick Notes', page_name='Notes on meeting y'))
         

    def test_create_page(self):
        page = onc.create_page(
            section_id='1-420c410c-927c-4e5f-b082-025e444b88e8',
            title="Hello 2",
            content_body="Hi are <b>you</b> okay</br><h1>Yes</h1>"
        )
        self.assertEqual(page.title, "Hello 2")


    def test_search_list(self):
        l = [1, 2, 3, 4, 5, 6]

        searched = onc._search_list(l, lambda x : x > 3)
        self.assertEqual(searched, 4)

        searched = onc._search_list(l, lambda x : x > 6)
        self.assertIsNone(searched)


    def test_load_page_content(self):
        p = Page(
            content_url="https://graph.microsoft.com/v1.0/users/608e5eda-301f-4291-bce3-af30a199a377/onenote/pages/1-6c4dfcd207024e7abee7569f2f9e3d57!22-420c410c-927c-4e5f-b082-025e444b88e8/content"
        )
        onc.load_page_content(p)
        print(p.page_content.get_text())


    def test_append_to_page(self):
        page_content = PageContent(html_body="to be appended")
        onc.append_to_page(
            page_id="1-0d8278dbf8674ec9980510ec15db6418!57-420c410c-927c-4e5f-b082-025e444b88e8", 
            page_content=page_content
        )


    def test_delete_page(self):
        page_to_be_deleted = "1-26a5b452aaad486a8104b1d9bf2a4af7!75-420c410c-927c-4e5f-b082-025e444b88e8"
        onc.delete_page(page_id=page_to_be_deleted)


    def test_copy_page(self):
        page_to_be_copied = "1-26a5b452aaad486a8104b1d9bf2a4af7!125-420c410c-927c-4e5f-b082-025e444b88e8"
        destination_section = "1-cd65ae70-3596-4544-835a-17c850d1c564"
        onc.copy_page(page_id=page_to_be_copied, section_id=destination_section)

    
    def test_move_page(self):
        # page = onc.create_page(section_id="1-420c410c-927c-4e5f-b082-025e444b88e8", title="Page to be moved", content_body="hi")
        page_to_be_moved = "1-26a5b452aaad486a8104b1d9bf2a4af7!125-420c410c-927c-4e5f-b082-025e444b88e8"
        destination_section = "1-cd65ae70-3596-4544-835a-17c850d1c564"
        onc.copy_page(page_id=page_to_be_moved, section_id=destination_section, move=True)


if __name__ == '__main__':
    unittest.main()
