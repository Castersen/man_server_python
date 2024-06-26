from subprocess import Popen, PIPE
from pathlib import Path
import re

from locations import TEMPLATE_PAGE, CACHE_DIR, CACHE, add_theme

class Potentials:
    def __init__(self, pot_str: str, name: str, section: str):
        self.pot_str = pot_str
        self.name = name
        self.section = section

    def __str__(self):
        return f'Could not find man page for {self.name} section {self.section} did you mean: {self.pot_str}'

def _run_command_and_get_output(command) -> str:
    try:
        with Popen(command, stdout=PIPE) as proc:
            return proc.stdout.read().decode('utf-8')
    except Exception:
        return None

def _find_page(name: str, section: str):
    locations: str = _run_command_and_get_output(['man', '-wa', name])

    if not locations:
        return None

    pot_str = ''
    for l in locations.rstrip('\n').split('\n'):
        n,s,_ = Path(l).name.split('.')
        pot_str += n + ' ' + s + ' '

        if section in s:
            return l

    return Potentials(pot_str, name, section) if pot_str else None

def _convert_page(path: str):
    return _run_command_and_get_output(['man2html', path])

def _post_process_page(page: str, theme: str, name: str):
    sections = re.findall(r'<DT>(<A\sHREF="[^"]*">[^<]*</A>)', page)
    section_html = ''.join(section for section in sections)

    with open(TEMPLATE_PAGE, 'r') as f:
        html_page = f.read().replace('{sections}', section_html).replace('{data}', page).replace('{name}', name)

    return add_theme(html_page, theme)

def _format_cache_name(name, section):
    return CACHE_DIR / (name + section + '.html')

def _page_in_cache(name, section):
    cache_name = _format_cache_name(name, section)
    if cache_name in CACHE:
        with open(cache_name, 'r') as f:
            return f.read()

    return None

def _cache_page(html_page, name, section):
    cache_name = _format_cache_name(name, section)
    with open(cache_name, 'w') as f:
        f.write(html_page)

    CACHE.append(cache_name)

def get_page(name: str, section: str, theme: str):
    cached_page = _page_in_cache(name, section)

    if cached_page:
        return _post_process_page(cached_page, theme, name)

    page_path = _find_page(name, section)

    if not page_path:
        return None

    if type(page_path) is Potentials:
        return page_path

    html_page = _convert_page(page_path)

    if not html_page:
        return None

    _cache_page(html_page, name, section)

    final_html_page = _post_process_page(html_page, theme, name)

    return final_html_page