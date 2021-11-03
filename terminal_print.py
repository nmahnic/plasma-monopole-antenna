# import os
from platform import system

def print_to_terminal(string, *args) -> None:
    """
    """
    if system() == 'Windows':
        print(100*"\n")
        # os.system('CLS')
    elif system() == 'Linux':
        print('\033[2J')
    elif system() == 'Darwin':
        pass
    print(string, *args)
