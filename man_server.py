import http.server
import socketserver
import urllib.parse
import argparse

from man_parser import get_page
from locations import STARTUP_PAGE, get_page_contents, ERROR_KEY

STARTUP_PAGE_CONTENTS = get_page_contents(STARTUP_PAGE)
PAGE_THEME = 'default'

class ManPageHandler(http.server.SimpleHTTPRequestHandler):
    def __setup_200_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def __send_start_page(self):
        self.__setup_200_headers()
        self.wfile.write(STARTUP_PAGE_CONTENTS.replace(ERROR_KEY, '').encode('utf-8'))

    def __send_start_page_with_error(self, error_msg: str):
        self.__setup_200_headers()
        self.wfile.write(STARTUP_PAGE_CONTENTS.replace(ERROR_KEY, error_msg).encode('utf-8'))

    def __parse_page_name(self, query: str):
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
                self.__send_start_page()
                return

            section, name = self.__parse_page_name(query)

            if not name:
                self.__send_start_page_with_error(f'Please provide man page name')
                return

            man_page_html = get_page(name, section, PAGE_THEME)

            if not man_page_html:
                self.__send_start_page_with_error(f'Could not find man page for {name}')
                return

            self.__setup_200_headers()
            self.wfile.write(man_page_html.encode('utf-8'))
        else:
            self.__send_start_page()
            return


def main():
    port = 8000
    host = 'localhost'

    parser = argparse.ArgumentParser(description='Man server options')
    parser.add_argument('-p', '--port', type=int, help='Set port')
    parser.add_argument('-t', '--theme', type=str, help='Set theme')

    args = parser.parse_args()

    if (args.port):
        port = args.port
    if (args.theme):
        global PAGE_THEME
        PAGE_THEME = args.theme

    print(f'Starting server at {host} port {port}')
    with socketserver.TCPServer((host, port), ManPageHandler) as server:
        server.serve_forever()

if __name__ == '__main__':
    main()