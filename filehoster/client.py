import flask
from pymongo import MongoClient
from multiprocessing import Process
from datetime import datetime
import os
import sys


if os.getenv("db"):
    client = MongoClient(os.getenv("db"))
else:
    print("No MongoDB found.\nExitting...")
    sys.exit()


db = client.users.files


# set these in your environment vars
# MUST
if os.getenv("adminuser") and os.getenv("adminpass"):
    adminuser = os.getenv("adminuser")
    adminpass = os.getenv("adminpass")
else:
    print("No admin credentials found.\nExitting...")
    sys.exit()


class WebClient(flask.Flask):
    def __init__(self, import_name=__name__):
        super().__init__(import_name)
        self.db = db
        self._tracker = {"send_file": [], "request": [], "jsonify": []}
        self._process = Process

    def send(self, *args, **kwargs):
        self._tracker["send_file"].append(datetime.now())
        return flask.send_file(*args, **kwargs)

    def get_requests(self):
        self._tracker["request"].append(datetime.now())
        return flask.request

    def json(self, *args, **kwargs):
        self._tracker["jsonify"].append(datetime.now())
        return flask.jsonify(*args, **kwargs)

    def get_start(self, *args, **kwargs):
        return Process(target=self.run, args=args, kwargs=kwargs)

    def get_creds(self):
        return os.getenv("adminuser"), os.getenv("adminpass")

    def render_html(self, html_location):
        if not isinstance(html_location, str):
            return "Invalid File"
        file = open(html_location, "r")
        return file.read()
