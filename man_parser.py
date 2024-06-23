#!/usr/bin/env python3

from subprocess import Popen, PIPE
from typing import List
import re

TEMPLATE = 'template.html'

def run_command_and_get_output(command) -> str:
    try:
        with Popen(command, stdout=PIPE) as proc:
            return proc.stdout.read().decode('utf-8')
    except Exception:
        return None

def find_page(name: str, section: int = None):
    section = '1' if not section else str(section)

    locations: List[str] = run_command_and_get_output(['whereis', name]).split()
    man = next((l for l in locations if l.endswith('.gz') and section in l), None)

    return man

def convert_page(path: str):
    return run_command_and_get_output(['man2html', path])

def post_process_page(page: str):
    sections = re.findall(r'<DT><A.*', page)
    section_html = ''

    for section in sections:
        id = re.search(r'(?<=\")[^"]*', section).group(0)
        title = re.search(r'(?<=\">)[^<]*', section).group(0)
        section_html += f'<a href=\"{id}\">{title}</a>'

    with open(TEMPLATE, 'r') as f:
        html_page = f.read().replace('{sections}', section_html).replace('{data}', page)

    return html_page