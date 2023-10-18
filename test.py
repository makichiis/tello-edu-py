
from typing import (List)
import subprocess
from sys import (
    stderr
)
import sys

def to_argv(s: str) -> List[str]:
    argv: List[str] = []
    current_arg = ''
    insq_flag: bool = False

    for char in s:
        if char.isspace() and not insq_flag:
            if current_arg:
                argv.append(current_arg)
                current_arg = ''
        elif char == '"':
            insq_flag = not insq_flag
        else:
            current_arg += char

    if current_arg:
        argv.append(current_arg)

    return argv


if __name__ == '__main__':
    py = sys.executable

    # this is kind of nasty but it works for now so it will
    # probably never be changed
    print('Resolving dependencies...')
    res = subprocess.call(to_argv(
        f'{py} -m pip install -r "requirements/dev"'))
    if res == 0: 
        res = subprocess.call(to_argv(
            f'{py} -m pip install -r tests/requirements.txt'))
    if res != 0:
        print('Pip failed. Are you in the right directory?', out=stderr)
        exit(1)
    print('Running Ruff...')
    res = subprocess.call(to_argv(f'{py} -m ruff check .'))
    if res != 0:
        print(f'Ruff test failed with exit code {res}', out=stderr)
        exit(2)
    print('Running pytest...')
    res = subprocess.call(to_argv(f'{py} -m pytest .'))
    if res != 0:
        print(f'pytest failed with exit code {res}.',
                'Are you in the right directory?',
                out=stderr)
        exit(3)
    print('All tests succeeded.')

