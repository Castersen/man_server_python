from pathlib import Path
import sys
import re

STARTUP_PAGE = 'startup_page.html'
TEMPLATE_PAGE = 'template.html'
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

def get_all_files_in_dirs(dirs: list[Path]):
    files = set()

    for dir in dirs:
        for file_path in dir.glob('**/*'):
            if file_path.is_dir():
                continue
            name = parse_man_name(file_path)
            section = parse_section(file_path)

            files.add(name + section)

    return sorted(files)

def parse_man_name(path: Path):
    name = path.name

    # Remove file extension
    suffix_pattern = re.compile(r'\.([glx]z|bz2|lzma|Z)$')
    name = re.sub(suffix_pattern, '', name)

    if '.' in name:
        name = '.'.join(name.split('.')[:-1])

    return name

def parse_section(path: Path):
    return path.parent.name.replace('man', '')

def add_theme(page: str, theme_name: str):
    theme_name = THEME_DIR / (theme_name + '.css')

    if theme_name not in THEMES:
        theme_name = DEFAULT_THEME

    return __add_theme(page, theme_name)

def __add_theme(page: str, theme: Path):
        with open(theme, 'r') as f:
            return page.replace(THEME_KEY, f.read())

def get_page_contents(page):
    with open(page, 'r') as f:
        return f.read()

class PageTheme:
    page_theme: str = 'default'

class StartPage:
    start_page = get_page_contents(STARTUP_PAGE)