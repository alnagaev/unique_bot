import json


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
        with open("group_dict.json", "w") as write_file:
            obj = dict()
            obj['chats'] = {}
            obj['chats'][key] = value
            json.dump(obj, write_file)


def json_key(key):
    with open('group_dict.json', 'r') as read_file:
        data = json.load(read_file)
        return data['chats'][key]


def chunks(l, n):
    n = max(1, n)
    return [l[i:i+n] for i in range(0, len(l), n)]


def show_keys():
    with open('group_dict.json', 'r') as read_file:
        data = json.load(read_file)
        return data['chats'].keys()