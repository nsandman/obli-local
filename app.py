import sys
import socketio

from sanic import Sanic
from inspect import isclass
from sanic_cors import CORS
from selenium import webdriver
from sanic.response import text
from os import getenv, listdir, path, getcwd

# from response import Response
# from urltask import UrlTask
# from constants import *

sio = socketio.AsyncServer(async_mode="sanic", cors_allowed_origins=[])
app = Sanic()
app.config["CORS_SUPPORTS_CREDENTIALS"] = True
CORS(app)
sio.attach(app)

chrome_driver = object()

@sio.event
async def event(sid, params):
    global mysql_prefs

    output = None

    if params["method"] != "core":
        statement = "output = {method}.{name}("
        try:
            if params["data"]:
                statement += '"""{data}"""'
        except:
            pass
        statement = (statement + ")").format(**params)
        exec(statement)
    else:
        output = await core_logic(params)

    return output if output else "ok"


def core_logic(params):
    pdata = params["data"]

    if params["name"] == "uploadFile":
        uploadForm = chrome_driver.find_element_by_css_selector("[obli-id=" + pdata["obli-id"] + "]")
        uploadForm.send_keys(pdata["path"])
    return

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
            exec("import " + module)

    driver_opts   = webdriver.chrome.options.Options()

    # TODO: make this work with non-Mac platforms
    driver_opts.add_argument("user-data-dir=" + path.expanduser("~") + "/Library/Application Support/Google/Chrome/Default")
    chrome_driver = webdriver.Chrome(options=driver_opts)

    PORT = getenv("PORT", 5726)
    app.run(host="0.0.0.0", port=PORT)

