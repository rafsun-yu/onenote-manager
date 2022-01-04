from datetime import datetime
import unittest
import pathlib
from bs4 import BeautifulSoup 
from ...clients import tools
from ...models.page import Page
from ..merge import group_by_week

class TestMerge(unittest.TestCase):
    def test_group_by_week(self):
        json_path = pathlib.Path(__file__).parent / 'pages.json'
        obj =  tools.load_dict(json_path)

        pages = []
        for o in obj['value']:
            pages.append(Page.from_json(json_obj=o))

        groups = group_by_week(pages)        

        for key, value in groups.items():
            print(key)
            for v in value:
                print(f"\t{v.created_date_time}")


if __name__ == '__main__':
    unittest.main()