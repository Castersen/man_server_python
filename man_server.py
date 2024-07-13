from http.server import SimpleHTTPRequestHandler, HTTPStatus
import socketserver
import urllib.parse
import argparse
from functools import lru_cache

from man_parser import get_page, setup_autocomplete
from locations import ERROR_KEY, POTENTIALS, THEMES, START_PAGE, get_page_contents, GlobalOptions
from errors import Perror, please_provide_name

class ManPageHandler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def __setup_200_headers(self, length: int):
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'text/html; charset=UTF-8')
        self.send_header('Content-Length', str(length))
        self.end_headers()

    @lru_cache(maxsize=32)
    def __get_start_page(self, error_msg: str) -> bytes:
        return START_PAGE.replace(ERROR_KEY, error_msg).encode('utf-8')

    def __send_start_page(self):
        payload = self.__get_start_page('')
        self.__setup_200_headers(len(payload))
        self.wfile.write(payload)

    def __send_start_page_with_error(self, error_msg: str):
        payload = self.__get_start_page(error_msg)
        self.__setup_200_headers(len(payload))
        self.wfile.write(payload)

    def __parse_page_name(self, query: str):
        if '+' in query:
            return query.split('+')

        return None, None

    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

        elif self.path.startswith('/query-potentials'):
            payload = get_page_contents(POTENTIALS).encode('utf-8')
            self.__setup_200_headers(len(payload))
            self.wfile.write(payload)

        elif self.path.startswith('/cgi-bin'):
            query = urllib.parse.urlparse(self.path).query

            if not query:
                self.__send_start_page()
                return

            section, name = self.__parse_page_name(query)

            if not name:
                self.__send_start_page_with_error(please_provide_name())
                return

            man_page_html = get_page(name, section)

            if type(man_page_html) is Perror:
                self.__send_start_page_with_error(man_page_html.message)
                return

            payload = man_page_html.encode('utf-8')
            self.__setup_200_headers(len(payload))
            self.wfile.write(payload)
        else:
            self.__send_start_page()
            return


def main():
    port = 8000
    host = 'localhost'
    allow_reuse = False

    parser = argparse.ArgumentParser(description='Man server options')
    parser.add_argument('-p', '--port', type=int, help='Set port')
    parser.add_argument('-i', '--host', type=str, help='Set host')
    parser.add_argument('-t', '--theme', type=str, help='Set theme')
    parser.add_argument('-r', '--refresh', action='store_true',
                        help='Update the generated list of man pages on your system')
    parser.add_argument('-a', '--allow', action='store_true', help='Allow reuse of address')
    parser.add_argument('-l', '--list', action='store_true',
                        help='list all theme names (this will not start the server)')
    parser.add_argument('-n', '--no-cache', action='store_true', help='Do not fetch pages from cache')

    args = parser.parse_args()

    if (args.list):
        print(', '.join(theme.name.rstrip('.css') for theme in THEMES))
        return
    if (args.port):
        port = args.port
    if (args.host):
        host = args.host
    if (args.allow):
        allow_reuse = args.allow
    if (args.theme):
        GlobalOptions.page_theme = args.theme
    if (args.no_cache):
        GlobalOptions.use_cache = False
    if (args.refresh or not POTENTIALS.is_file()):
        setup_autocomplete()

    class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        daemon_threads = True
        allow_reuse_address = allow_reuse

    print(f'Starting server at {host} port {port}')
    with ThreadingTCPServer((host, port), ManPageHandler) as server:
        server.serve_forever()

if __name__ == '__main__':
    main()