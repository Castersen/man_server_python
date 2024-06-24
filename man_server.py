import http.server
import socketserver
import urllib.parse
import html

from man_parser import get_page

PORT = 8000
HOST = 'localhost'

class ManPageHandler(http.server.SimpleHTTPRequestHandler):
    def send_start_page(self):
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
                <label for="section">Select Section:</label>
                <select id="section" name="section">
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                    <option value="6">6</option>
                    <option value="7">7</option>
                    <option value="8">8</option>
                </select>
                <input type="submit" value="Get Man Page">
            </form>
        </body>
        </html>
        '''
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
            print(query)

            section, name = self.parse_page_name(query)
            print(f'Section: {section}, Name: {name}')

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