from subprocess import Popen, PIPE
from pathlib import Path
import sys
import re
from typing import Tuple, List

from locations import TEMPLATE_PAGE, CACHE_DIR, CACHE, POTENTIALS, UseCache, add_theme
from errors import Perror, could_not_run_command, could_not_find, could_not_find_potentials

def _parse_man_name_and_section(path: Path) -> Tuple[str, str]:
    name = path.name

    # Remove file extension
    suffix_pattern = re.compile(r'\.([glx]z|bz2|lzma|Z)$')
    name = re.sub(suffix_pattern, '', name)

    if '.' in name:
        name = '.'.join(name.split('.')[:-1])

    return name, path.parent.name.replace('man', '')

def setup_autocomplete() -> None:
    man_dirs = _run_command_and_get_output(['manpath', '-q'])

    if type(man_dirs) is Perror:
        print(man_dirs.message)
        return

    dirs = list(map(Path, man_dirs.rstrip('\n').split(':')))

    pages = set()
    for dir in dirs:
        for file_path in dir.glob('**/*'):
            if file_path.is_dir():
                continue
            name, section = _parse_man_name_and_section(file_path)
            pages.add(name + section)

    with open(POTENTIALS, 'w') as f:
        f.write(','.join(page for page in sorted(pages)))

def _run_command_and_get_output(command: List[str]) -> str | Perror:
    try:
        with Popen(command, stdout=PIPE) as proc:
            return proc.stdout.read().decode('utf-8')
    except Exception:
        return could_not_run_command(' '.join(command))

def _find_page(name: str, section: str) -> str | Perror:
    locations: str = _run_command_and_get_output(['man', '-wa', name])

    if not locations:
        return could_not_find(name, section)

    pot_str = set()
    for l in locations.rstrip('\n').split('\n'):
        pot_name, pot_section = _parse_man_name_and_section(Path(l))
        pot_str.add(f'{pot_name} {pot_section}')

        if section in pot_section:
            return l

    return could_not_find_potentials(name, section, ' '.join(pot_str))

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

def _fetch_page_from_cache(cache_path: Path) -> str:
    with open(cache_path, 'r') as f:
        return f.read()

def _page_in_cache(cache_path: Path) -> bool:
    return cache_path in CACHE

def _cache_page(html_page: str, cache_path: Path) -> None:
    with open(cache_path, 'w') as f:
        f.write(html_page)

    CACHE.append(cache_path)

def get_page(name: str, section: str, theme: str) -> str | Perror:
    cache_path = _format_cache_name(name, section)

    if UseCache.cache and _page_in_cache(cache_path):
        return _post_process_page(_fetch_page_from_cache(cache_path), theme, name)

    page_path = _find_page(name, section)

    if type(page_path) is Perror:
        return page_path

    html_page = _convert_page(page_path)

    if type(html_page) is Perror:
        return html_page

    _cache_page(html_page, cache_path)

    final_html_page = _post_process_page(html_page, theme, name)

    return final_html_page