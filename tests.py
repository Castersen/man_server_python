import unittest
from man_parser import get_page, Potentials

DEFAULT_THEME = 'default'

class TestFindPage(unittest.TestCase):
    def test_find_success(self):
        result = get_page('man', '1', DEFAULT_THEME)
        self.assertTrue(isinstance(result, str))

    def test_find_failure(self):
        result = get_page('fake', '1', DEFAULT_THEME)
        self.assertTrue(result == None)

    def test_find_possible(self):
        result = get_page('man', '10', DEFAULT_THEME)
        self.assertTrue(isinstance(result, Potentials))

if __name__ == '__main__':
    unittest.main()