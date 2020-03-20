import json
import os



class WrongDirectoryError(FileNotFoundError):
    pass


def json_add(key, value):
    try:
        with open("group_dict.json", 'r') as f:
            try:
                obj = json.load(f)
                obj['chats'][key] = value
            except ValueError:
                obj = dict()
                obj['chats'] = {}
                obj['chats'][key] = value

            with open("group_dict.json", "w") as write_file:
                json.dump(obj, write_file)

    except FileNotFoundError:
        if os.path.basename(os.getcwd()) != 'unique_bot':
            raise WrongDirectoryError
        else:
            with open("group_dict.json", "w") as write_file:
                obj = dict()
                obj['chats'] = {}
                obj['chats'][key] = value
                json.dump(obj, write_file)


def json_key(key):
    try:
        with open('group_dict.json', 'r') as read_file:
            data = json.load(read_file)
            return data['chats'][key]

    except FileNotFoundError:
        if os.path.basename(os.getcwd()) != 'unique_bot':
            raise WrongDirectoryError
            
            
def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]


def show_keys():
    try:
        with open('group_dict.json', 'r') as read_file:
            data = json.load(read_file)
            return data['chats'].keys()
    except FileNotFoundError:
        if os.path.basename(os.getcwd()) != 'unique_bot':
            raise WrongDirectoryError
