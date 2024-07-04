from pathlib import Path
import sys

def get_page_contents(page: str) -> str:
    with open(page, 'r') as f:
        return f.read()

START_PAGE = get_page_contents('startup_page.html')
TEMPLATE_PAGE = get_page_contents('template.html')
ERROR_KEY = '{error}'

if sys.platform.startswith('darwin'):
    THEME_DIR = Path('themes_mac')
else:
    THEME_DIR = Path('themes')

THEMES = [theme for theme in THEME_DIR.iterdir()]
DEFAULT_THEME = THEME_DIR / 'default.css'
THEME_KEY = '/*Theme*/'

CACHE_DIR = Path('cache')
CACHE = [man_page for man_page in CACHE_DIR.iterdir()]

POTENTIALS = Path('man_pages.txt')

def add_theme(page: str):
    theme_name = THEME_DIR / (GlobalOptions.page_theme + '.css')

    if theme_name not in THEMES:
        theme_name = DEFAULT_THEME

    with open(theme_name, 'r') as f:
        return page.replace(THEME_KEY, f.read())

class GlobalOptions:
    page_theme: str = 'default'
    use_cache: bool = True