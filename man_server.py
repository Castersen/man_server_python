import http.server
import socketserver
import urllib.parse

from man_parser import get_page
from locations import STARTUP_PAGE, get_page_contents

STARTUP_PAGE_CONTENTS = get_page_contents(STARTUP_PAGE)

PORT = 8000
HOST = 'localhost'

class ManPageHandler(http.server.SimpleHTTPRequestHandler):
    def send_start_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html_content = STARTUP_PAGE_CONTENTS
        self.wfile.write(html_content.encode('utf-8'))

    def parse_page_name(self, query: str):
        if '&' in query:
            n,s = query.split('&')
            return s.split('=')[-1], n.split('=')[-1]

        if '+' in query:
            return query.split('+')

        return None, query

    def do_GET(self):
        if self.path.startswith('/cgi-bin'):
            query = urllib.parse.urlparse(self.path).query
            section, name = self.parse_page_name(query)

            if not name:
                self.send_start_page()
                return

            man_page_html = get_page(name, section)

            if not man_page_html:
                self.send_error(404, f'Error fetching man page for {name}')
                return

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(man_page_html.encode('utf-8'))
        else:
            self.send_start_page()
            return

with socketserver.TCPServer((HOST, PORT), ManPageHandler) as server:
    server.serve_forever()