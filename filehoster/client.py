#    This file is part of FileHoster.

#    FileHoster is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    FileHoster is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with FileHoster.  If not, see <https://www.gnu.org/licenses/>.


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
