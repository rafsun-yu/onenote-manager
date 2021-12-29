from datetime import datetime
import unittest
import pathlib
from bs4 import BeautifulSoup 
from ..page import Page, PageContent

class TestPageContent(unittest.TestCase):
    def test_set_soup_title(self):
        pc = PageContent()
        pc._set_soup_title('hello')
        soup = BeautifulSoup(pc.get_html(), 'html.parser')
        self.assertEqual('hello', soup.title.string)


    def test_set_soup_created(self):
        pc = PageContent()

        pc._set_soup_created('2007-03-01T13:00:00')
        soup = BeautifulSoup(pc.get_html(), 'html.parser')
        self.assertEqual('2007-03-01T13:00:00', soup.select('meta[name=created]')[0]['content'])

        dt = datetime(year=2001, month=1, day=1)
        pc._set_soup_created(created_datetime=dt)
        soup = BeautifulSoup(pc.get_html(), 'html.parser')
        self.assertEqual(dt.isoformat(), soup.select('meta[name=created]')[0]['content'])


    def test_append(self):
        pc1 = PageContent(html="Hello 1")
        pc3 = PageContent()
        
        pc3.append(page_content=pc1)
        pc3.append(separator='--', page_content=pc1)
        pc3.append(html='<b>hello 2</b>')

        self.assertEqual(
            b"Hello 1</br>--</br>Hello 1</br><b>hello 2</b>",
            pc3._get_soup_content().encode_contents()
        )

if __name__ == '__main__':
    unittest.main()