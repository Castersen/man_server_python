from pathlib import Path

STARTUP_PAGE = 'startup_page.html'
TEMPLATE_PAGE = 'template.html'
ERROR_KEY = '{error}'

THEME_DIR = Path('themes')
THEMES = [theme for theme in THEME_DIR.iterdir()]
DEFAULT_THEME = THEME_DIR / 'default.css'
THEME_KEY = '/*Theme*/'

CACHE_DIR = Path('cache')
CACHE = [man_page for man_page in CACHE_DIR.iterdir()]

def add_theme(page: str, theme_name: str):
    theme_name = __format_theme_name(theme_name)

    if not theme_name or theme_name not in THEMES:
        return __add_theme(page, DEFAULT_THEME)

    return __add_theme(page, theme_name)

def __add_theme(page: str, theme):
        with open(theme, 'r') as f:
            return page.replace(THEME_KEY, f.read())

def __format_theme_name(theme_name: str):
    if not theme_name:
        return None

    return THEME_DIR / (theme_name + '.css')

def get_page_contents(page):
    with open(page, 'r') as f:
        return f.read()

class PageTheme:
    page_theme:str = 'default'

class StartPage:
    start_page = get_page_contents(STARTUP_PAGE)