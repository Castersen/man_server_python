import http.server
import socketserver
import urllib.parse
import html
from man_parser import find_page, convert_page, post_process_page

PORT = 8000
HOST = 'localhost'

class ManPageHandler(http.server.SimpleHTTPRequestHandler):
    def parse_page_name(self, query: str):
        if '=' in query:
            return None, query.split('=')[-1]

        if '+' in query:
            return query.split('+')

        return None, query

    def do_GET(self):
        if self.path.startswith('/cgi-bin'):
            query = urllib.parse.urlparse(self.path).query
            print(query)

            section, name = self.parse_page_name(query)
            print(f'Section: {section}, Name: {name}')

            if not name:
                self.send_error(400, 'Please provide a name for the man page.')
                return

            man_page_html = post_process_page(convert_page(find_page(name, section)))

            if not man_page_html:
                self.send_error(404, f'Error fetching man page for {html.escape(name)}.')
                return

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(man_page_html.encode('utf-8'))
        else:
            # Handle the root path
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = '''
            <html>
            <head><title>Man Page Server</title></head>
            <body>
                <h1>Man Page Server</h1>
                <form action="/cgi-bin" method="get">
                    <label for="man2html">Enter Command:</label>
                    <input type="text" id="man2html" name="man2html">
                    <input type="submit" value="Get Man Page">
                </form>
            </body>
            </html>
            '''
            self.wfile.write(html_content.encode('utf-8'))
            return

with socketserver.TCPServer((HOST, PORT), ManPageHandler) as server:
    server.serve_forever()