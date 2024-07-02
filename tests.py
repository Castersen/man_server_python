import unittest
import socketserver
import threading
import urllib.request
from pathlib import Path

from man_parser import get_page, _page_in_cache, _parse_man_name_and_section
from man_server import ManPageHandler
from locations import ERROR_KEY, StartPage
from errors import Perror, could_not_find, please_provide_name

DEFAULT_THEME = 'default'

class TestParsing(unittest.TestCase):
    def test_parse_path_correctly(self):
        sys_conf_n, sys_conf_s = _parse_man_name_and_section(Path('/usr/share/man/man5/systemd-system.conf.5.gz'))
        man_n, man_s = _parse_man_name_and_section(Path('/usr/share/man/man1/man.1.gz'))
        self.assertEqual(sys_conf_n, 'systemd-system.conf')
        self.assertEqual(sys_conf_s, '5')
        self.assertEqual(man_n, 'man')
        self.assertEqual(man_s, '1')

class TestFindPage(unittest.TestCase):
    def test_find_success(self):
        result = get_page('man', '1', DEFAULT_THEME)
        self.assertTrue(isinstance(result, str))
        result = _page_in_cache('man', '1')
        self.assertTrue(result != None)

    def test_find_failure(self):
        result = get_page('fake', '1', DEFAULT_THEME)
        self.assertTrue(isinstance(result, Perror))
        self.assertTrue(could_not_find('fake', '1').message == result.message)

    def test_find_possible(self):
        result = get_page('man', '10', DEFAULT_THEME)
        self.assertTrue(isinstance(result, Perror))

class ManTCPTestServer(socketserver.TCPServer):
    allow_reuse_address = True

PORT = 8000
class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ManTCPTestServer(('localhost', PORT), ManPageHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    def test_startup_page_default(self):
        with urllib.request.urlopen(f'http://localhost:{PORT}') as response:
            self.assertEqual(response.status, 200)
            page_bytes = bytes(StartPage.start_page.replace(ERROR_KEY, '').encode('utf-8'))
            self.assertEqual(response.read(), page_bytes)

    def test_startup_page_error(self):
        with urllib.request.urlopen(f'http://localhost:{PORT}/cgi-bin/man/man2html?10+fake') as response:
            self.assertEqual(response.status, 200)
            error_msg = could_not_find('fake', '10').message
            error_bytes = bytes(StartPage.start_page.replace(ERROR_KEY, error_msg).encode('utf-8'))
            self.assertEqual(response.read(), error_bytes)

    def test_startup_page_no_name(self):
        with urllib.request.urlopen(f'http://localhost:{PORT}/cgi-bin/man/man2html?10') as response:
            self.assertEqual(response.status, 200)
            error_msg = please_provide_name()
            error_bytes = bytes(StartPage.start_page.replace(ERROR_KEY, error_msg).encode('utf-8'))
            self.assertEqual(response.read(), error_bytes)

    def test_valid_page(self):
        with urllib.request.urlopen(f'http://localhost:{PORT}/cgi-bin/man/man2html?1+man') as response:
            self.assertEqual(response.status, 200)
            converted_man_page = bytes(get_page('man', '1', DEFAULT_THEME).encode('utf-8'))
            self.assertEqual(response.read(), converted_man_page)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

if __name__ == '__main__':
    unittest.main()