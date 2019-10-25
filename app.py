import sys
import socketio

from sys import modules
from sanic import Sanic
from selenium import webdriver
from os import getenv, listdir, path, getcwd

# from response import Response
# from urltask import UrlTask
# from constants import *

sio = socketio.AsyncServer(async_mode="sanic", cors_allowed_origins=[])
app = Sanic()
app.config["CORS_SUPPORTS_CREDENTIALS"] = True
sio.attach(app)

chrome_driver = object()

@sio.event
async def event(sid, params):
    output = None
    if params["method"] != "core":
        interface = Interface(sid, params["method"])
        module_method = getattr(modules[params["method"]], params["name"])

        try:
            output = await module_method(interface)
        except TypeError:
            output = await module_method(interface, params["data"])
    else:
        output = await core_logic(params)

    return output


def core_logic(params):
    pname = params["name"]
    pdata = params["data"]

    if pname == "uploadFile":
        filepath = pdata["path"]

        tf = tempfile.NamedTemporaryFile()
        if filepath.startswith("http") or filepath.startswith("ftp"):
            filedata = urllib.request.urlopen(filepath)
            tf.write(filedata.read())
            filepath = tf.name

            uploadForm = chrome_driver.find_element_by_css_selector("[obli-id=" + pdata["obli-id"] + "]")
            uploadForm.send_keys(filepath)
    return

class Interface():
    def __init__(self, sid, name):
        self.sid  = sid
        self.name = name

    async def send(self, event, data):
        await sio.emit("event", {
            "event": event,
            "data":  data,
            "me": self.name
        }, room=self.sid)

@sio.event
async def connect(sid, _):
    print("connect ", sid)

@sio.event
async def disconnect(sid):
    print("disconnect ", sid)

if __name__ == "__main__":
    modules_dir = path.join(getcwd(), "modules")
    sys.path.append(modules_dir)
    for module in listdir(modules_dir):
        if path.isdir(path.join(modules_dir, module)):
            print("Loading module", module)
            __import__(module)

    driver_opts   = webdriver.chrome.options.Options()

    # TODO: make this work with non-Mac platforms
    driver_opts.add_argument("user-data-dir=" + path.expanduser("~") + "/Library/Application Support/Google/Chrome/Default")
    chrome_driver = webdriver.Chrome(options=driver_opts)

    PORT = getenv("PORT", 5726)
    app.run(host="0.0.0.0", port=PORT)

