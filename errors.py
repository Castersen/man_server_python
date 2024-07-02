from dataclasses import dataclass

@dataclass
class Perror:
    message: str

def could_not_find(name: str, section: str) -> Perror:
    return Perror(f'Could not find man page {name} for section {section}')

def could_not_find_potentials(name: str, section: str, potentials: str) -> Perror:
    return Perror(f'Could not find man page {name} for section {section} did you mean {potentials}')

def please_provide_name() -> str:
    return 'Please provide man page name'

def could_not_run_command(command: str) -> Perror:
    return Perror(f'Fatal: Could not run command {command}')