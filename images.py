from pathlib import Path
import os
from contextlib import contextmanager

@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def get_unique(path, chat):
    print(os.getcwd())
    with cwd(os.path.join(path, str(chat))):

        photos = [(open(i, 'rb'), os.path.getsize(i)) for i in os.listdir() if i.endswith(('.png', '.jpg'))]
        seen, pairs = set(), []
        for a, b in photos:
            if b not in seen:
                pairs.append(a)
            seen.add(b)

        return pairs

