from pathlib import Path
import os


def get_unique(path, chat):
    if os.path.basename(os.getcwd()) != path:
        os.chdir(os.path.join(path, str(chat)))
    photos = [(open(i, 'rb'), os.path.getsize(i)) for i in os.listdir() if i.endswith(('.png', '.jpg'))]
    seen, pairs = set(), []
    for a, b in photos:
        if b not in seen:
            pairs.append((a))
        seen.add(b)

    return pairs


