from subprocess import Popen, PIPE
import re

from locations import add_theme, TEMPLATE_PAGE

def __run_command_and_get_output(command) -> str:
    try:
        with Popen(command, stdout=PIPE) as proc:
            return proc.stdout.read().decode('utf-8')
    except Exception:
        return None

def __find_page(name: str, section: str):
    locations: str = __run_command_and_get_output(['whereis', name])

    if not locations:
        return None

    for l in locations.split():
        if l.endswith('.gz') and section in l:
            return l

    return None

def __convert_page(path: str):
    return __run_command_and_get_output(['man2html', path])

def __post_process_page(page: str, theme: str):
    sections = re.findall(r'<DT><A.*', page)
    section_html = ''

    for section in sections:
        start = section.find('"')
        end = section[start:].find('<')
        id, title = section[start:start+end].split('>')
        section_html += f'<a href={id}>{title}</a>'

    with open(TEMPLATE_PAGE, 'r') as f:
        html_page = f.read().replace('{sections}', section_html).replace('{data}', page)

    return add_theme(html_page, theme)

def get_page(name: str, section: str, theme: str):
    page_path = __find_page(name, section)

    if not page_path:
        return None

    html_page = __convert_page(page_path)

    if not html_page:
        return None

    final_html_page = __post_process_page(html_page, theme)

    return final_html_page