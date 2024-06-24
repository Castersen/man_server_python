import http.server
import socketserver
import urllib.parse

from man_parser import get_page
from locations import STARTUP_PAGE, get_page_contents, ERROR_KEY

STARTUP_PAGE_CONTENTS = get_page_contents(STARTUP_PAGE)

PORT = 8000
HOST = 'localhost'

class ManPageHandler(http.server.SimpleHTTPRequestHandler):
    def __setup_200_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def send_start_page(self):
        self.__setup_200_headers()
        self.wfile.write(STARTUP_PAGE_CONTENTS.replace(ERROR_KEY, '').encode('utf-8'))

    def send_start_page_with_error(self, error_msg: str):
        self.__setup_200_headers()
        self.wfile.write(STARTUP_PAGE_CONTENTS.replace(ERROR_KEY, error_msg).encode('utf-8'))

    def parse_page_name(self, query: str):
        if '&' in query:
            n,s = query.split('&')
            return s.split('=')[-1], n.split('=')[-1]

        if '+' in query:
            return query.split('+')

        return None, None

    def do_GET(self):
        if self.path.startswith('/cgi-bin'):
            query = urllib.parse.urlparse(self.path).query

            if not query:
                self.send_start_page()
                return

            section, name = self.parse_page_name(query)

            if not name:
                self.send_start_page_with_error(f'Please provide man page name')
                return

            man_page_html = get_page(name, section)

            if not man_page_html:
                self.send_start_page_with_error(f'Could not find man page for {name}')
                return

            self.__setup_200_headers()
            self.wfile.write(man_page_html.encode('utf-8'))
        else:
            self.send_start_page()
            return

with socketserver.TCPServer((HOST, PORT), ManPageHandler) as server:
    server.serve_forever()