from pathlib import Path

STARTUP_PAGE = 'startup_page.html'
def get_page_contents(page):
    with open(page, 'r') as f:
        return f.read()