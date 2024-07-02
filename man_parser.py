from subprocess import Popen, PIPE
from pathlib import Path
import sys
import re

from locations import TEMPLATE_PAGE, CACHE_DIR, CACHE, POTENTIALS, add_theme, get_all_files_in_dirs, parse_man_name, parse_section
from errors import Perror, could_not_run_command, could_not_find, could_not_find_potentials

def setup_autocomplete() -> None:
    man_dirs = _run_command_and_get_output(['manpath', '-q'])

    if type(man_dirs) is Perror:
        print(man_dirs.message)
        return

    files = get_all_files_in_dirs(list(map(Path, man_dirs.rstrip('\n').split(':'))))

    with open(POTENTIALS, 'w') as f:
        f.write(','.join(file for file in files))

def _run_command_and_get_output(command: list[str]) -> str | Perror:
    try:
        with Popen(command, stdout=PIPE) as proc:
            return proc.stdout.read().decode('utf-8')
    except Exception:
        return could_not_run_command(' '.join(command))

def _find_page(name: str, section: str) -> str | Perror:
    locations: str = _run_command_and_get_output(['man', '-wa', name])

    if not locations:
        return could_not_find(name, section)

    pot_str = ''
    for l in locations.rstrip('\n').split('\n'):
        pot_name = parse_man_name(Path(l))
        pot_section  = parse_section(Path(l))
        pot_str += pot_name + ' ' + pot_section + ' '

        if section in pot_section:
            return l

    return could_not_find_potentials(name, section, pot_str)

def _convert_page(path: str) -> str | Perror:
    if sys.platform.startswith('darwin'):
        return _run_command_and_get_output(['mandoc', '-O', 'toc,fragment,man=/cgi-bin?%S+%N', '-T', 'html', path])
    else:
        return _run_command_and_get_output(['man2html', path])

def _post_process_page(page: str, theme: str, name: str) -> str:
    if sys.platform.startswith('darwin'):
        sections = re.findall(r'(<a class="permalink"\shref="[^"]*">[^<]*</a>)', page, re.IGNORECASE)
    else:
        sections = re.findall(r'<dt>(<a\shref="[^"]*">[^<]*</a>)', page, re.IGNORECASE)

    section_html = ''.join(section for section in sections)

    with open(TEMPLATE_PAGE, 'r') as f:
        html_page = f.read().replace('{sections}', section_html).replace('{data}', page).replace('{name}', name)

    return add_theme(html_page, theme)

def _format_cache_name(name: str, section: str) -> Path:
    return CACHE_DIR / (name + section + '.html')

def _page_in_cache(name: str, section: str) -> str | None:
    cache_name = _format_cache_name(name, section)
    if cache_name in CACHE:
        with open(cache_name, 'r') as f:
            return f.read()

    return None

def _cache_page(html_page: str, name: str, section: str) -> None:
    cache_name = _format_cache_name(name, section)
    with open(cache_name, 'w') as f:
        f.write(html_page)

    CACHE.append(cache_name)

def get_page(name: str, section: str, theme: str) -> str | Perror:
    cached_page = _page_in_cache(name, section)

    if cached_page:
        return _post_process_page(cached_page, theme, name)

    page_path = _find_page(name, section)

    if type(page_path) is Perror:
        return page_path

    html_page = _convert_page(page_path)

    if type(html_page) is Perror:
        return html_page

    _cache_page(html_page, name, section)

    final_html_page = _post_process_page(html_page, theme, name)

    return final_html_page