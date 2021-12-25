import unittest
import pathlib
from ..model import Model
from ..notebook import Notebook


class TestModel(unittest.TestCase):
    def test_from_json(self):
        test_data_path = pathlib.Path(__file__).parent / 'data/notebook.json'
        with test_data_path.open() as f:
            json_str = f.read()
            n = Notebook.from_json(json_str=json_str)
            self.assertEqual(n.id, '1-e13f257d-78c6-46cf-ae8c-13686517ac5f')
            self.assertEqual(n.created_date_time, '2017-09-15T01:15:44Z')
            self.assertEqual(n.display_name, 'Megan @ Work')
            self.assertEqual(n.sections_url, 'https://graph.microsoft.com/v1.0/users/48d31887-5fad-4d73-a9f5-3c356e68a038/onenote/notebooks/1-e13f257d-78c6-46cf-ae8c-13686517ac5f/sections')


if __name__ == '__main__':
    unittest.main()