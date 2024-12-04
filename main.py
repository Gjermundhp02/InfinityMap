import asyncio
import os
from mitmproxy import options
from mitmproxy.tools import main, dump
from mitmproxy.http import HTTPFlow
import threading
import json
import readline


commands = {
    "show-objects": lambda: print(objects),
    "show-paths": lambda: print(paths),
    "exit": lambda: None,
}

def completer(text, state):
    options = [i for i in commands.keys() if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

# {name: {emoji: str, isNew: bool, index: keyof paths}}
objects = {
    "Water": {"emoji": "💧", "isNew": False, "creates": [], "createdBy": []},
    "Fire":  {"emoji": "🔥", "isNew": False, "creates": [], "createdBy": []},
    "Earth": {"emoji": "🌍", "isNew": False, "creates": [], "createdBy": []},
    "Wind":  {"emoji": "🌬️", "isNew": False, "creates": [], "createdBy": []},
}
objectsLoaded = False
try:
    with open('objects.json', 'r') as f:
        objects = json.loads(f.read())
        objectsLoaded = True
except FileNotFoundError:
    print('No objects.json file found. Will try to regenerate from paths.json\n')

# [{first: str, second: str, result: str}]
paths = []
try:
    with open('paths.json', 'r') as f:
        paths = json.loads(f.read())
        if not objectsLoaded:
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

class MyCustomAddon:
    async def response(self, flow: HTTPFlow):
        if flow.request.host == 'neal.fun' and flow.request.path_components == ('api', 'infinite-craft', 'pair') and flow.response.headers['Content-Type'] == 'application/json':
            resJson = flow.response.json()
            path = {
                "first": flow.request.query['first'],
                "second": flow.request.query['second'],
                "result": resJson['result']
            }
            if path not in paths:
                paths.append({
                    "first": flow.request.query['first'],
                    "second": flow.request.query['second'],
                    "result": resJson['result']
                })
                if flow.request.query['first'] in objects:
                    objects[flow.request.query['first']]['creates'].append(len(paths) - 1)
                if flow.request.query['second'] in objects:
                    objects[flow.request.query['second']]['creates'].append(len(paths) - 1)
                if resJson['result'] in objects:
                    objects[resJson['result']]['createdBy'].append(len(paths) - 1)
                    if objects[resJson['result']]['emoji'] != resJson['emoji']: # If the emoji has 
                        objects[resJson['result']]['emoji'] = resJson['emoji']
                else:
                    objects[resJson['result']] = {"emoji": resJson['emoji'], "isNew": resJson['isNew'], "creates": [], "createdBy": [len(paths) - 1]}
            print(paths, objects)
            

class ProxyServer(object):

    def __init__(self, proxy_host='localhost', proxy_port=8080):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.master = None

    async def start_dump(self):
        opts = options.Options(listen_host=self.proxy_host, listen_port=self.proxy_port)

        self.master = dump.DumpMaster(
            opts,
            with_termlog=False,
            with_dumper=False,
        )
        self.master.addons.add(MyCustomAddon())
        try:
            print("Starting proxy server")
            await self.master.run()
        except asyncio.exceptions.CancelledError:
            self.stop()
        return self.master
    
    def stop(self):
        with open('paths.json', 'w') as f:
                f.write(json.dumps(paths))
        with open('objects.json', 'w') as f:
            f.write(json.dumps(objects))
        self.master.shutdown()
        print('Stopping proxy server')
    
    def input_handler(self):
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer)
        while True:
            inp = input()
            match inp:
                case 'show-objects':
                    commands['show-objects']()
                case 'show-paths':
                    commands['show-paths']()
                case 'exit' | 'q':
                    self.stop()
                    break

    def start(self):
        pThread = threading.Thread(target=lambda: asyncio.run(self.start_dump()))
        pThread.daemon = True
        pThread.start()
        try:
            self.input_handler()
        except KeyboardInterrupt:
            self.stop()
            pThread.join()


ProxyServer().start()