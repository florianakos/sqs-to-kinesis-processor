from sys import stderr

def die(*args, **kwargs):
    print(*args, file=stderr, **kwargs)
    exit(1)

def red(txt):
    return f"\033[91m{txt}\033[0m"

def green(txt):
    return f"\033[92m{txt}\033[0m"

def blue(txt):
    return f"\033[94m{txt}\033[0m"
