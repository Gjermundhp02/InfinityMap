import json

def loadState():
    # {name: {emoji: str, isNew: bool, index: keyof paths}}
    objects = {
        "Water": {"emoji": "💧", "isNew": False, "creates": [], "createdBy": []},
        "Fire":  {"emoji": "🔥", "isNew": False, "creates": [], "createdBy": []},
        "Earth": {"emoji": "🌍", "isNew": False, "creates": [], "createdBy": []},
        "Wind":  {"emoji": "🌬️", "isNew": False, "creates": [], "createdBy": []},
    }
    # [{first: str, second: str, result: str}]
    paths = []

    objectsLoaded = False
    try:
        with open('objects.json', 'r') as f:
            objects = json.loads(f.read())
            objectsLoaded = True
    except FileNotFoundError:
        print('No objects.json file found. Will try to regenerate from paths.json\n')

    try:
        with open('paths.json', 'r') as f:
            paths = json.loads(f.read())
            if not objectsLoaded:
                if len(paths) == 0:
                    print('No paths in paths.json file.')
                else:
                    for path in paths:
                        if path['first'] in objects:
                            objects[path['first']]['creates'].append(paths.index(path))
                        if path['second'] in objects:
                            objects[path['second']]['creates'].append(paths.index(path))
                        if path['result'] in objects:
                            objects[path['result']]['createdBy'].append(paths.index(path))
                        else:
                            objects[path['result']] = {"emoji": None, "isNew": None, "creates": [], "createdBy": [paths.index(path)]}
                    print("Regenerated objects.json file from paths.json file.",
                        "Emojis and isNew values are lost.",
                        "Emojis will be added if the object is created again.", sep='\n')
    except FileNotFoundError:
        print('No paths.json file found.')
        if objectsLoaded:
            print('Could not regenerate paths.json file.')

    return objects, paths